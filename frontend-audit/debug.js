const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
    let report = `# RUNTIME DEBUG REPORT\n\n`;
    
    report += `## Environment\n`;
    report += `* Testing frontend at: http://localhost:3000\n`;
    report += `* Testing backend at: http://127.0.0.1:8000/api/v1\n\n`;

    const browser = await puppeteer.launch({ 
        headless: "new",
        executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe"
    });
    const page = await browser.newPage();
    
    let networkRequests = [];
    let consoleErrors = [];
    
    // Capture console messages
    page.on('console', msg => {
        if (msg.type() === 'error' || msg.type() === 'warning') {
            consoleErrors.push(`[${msg.type().toUpperCase()}] ${msg.text()}`);
        }
    });

    // Capture network requests
    page.on('request', request => {
        networkRequests.push({
            id: request._requestId,
            url: request.url(),
            method: request.method(),
            headers: request.headers(),
            postData: request.postData(),
            response: null
        });
    });

    page.on('response', async response => {
        const req = networkRequests.find(r => r.url === response.url() && r.method === response.request().method());
        if (req) {
            req.response = {
                status: response.status(),
                headers: response.headers(),
                body: ''
            };
            try {
                // Ignore preflight options and non-json bodies
                if (response.request().method() !== 'OPTIONS' && response.headers()['content-type']?.includes('application/json')) {
                    req.response.body = await response.text();
                }
            } catch (e) {
                req.response.body = '[Could not read body]';
            }
        }
    });

    console.log("Navigating to login...");
    await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' });
    await new Promise(r => setTimeout(r, 2000));

    console.log("Logging in...");
    try {
        const usernameInput = await page.$('input[name="username"]') || await page.$('input[type="text"]') || await page.$('input[type="email"]');
        const passwordInput = await page.$('input[name="password"]') || await page.$('input[type="password"]');
        
        if (usernameInput) await usernameInput.type('muskankumar');
        if (passwordInput) await passwordInput.type('Muskan@7842');
        
        const submitBtn = await page.$('button[type="submit"]') || await page.$('button');
        if (submitBtn) {
            await submitBtn.click();
            await new Promise(r => setTimeout(r, 5000)); // wait for login and navigation
        }
    } catch(e) {
        console.error("Login failed or inputs not found", e);
    }

    console.log("Waiting for dashboard requests...");
    await new Promise(r => setTimeout(r, 3000)); // give it a few seconds
    
    await page.screenshot({ path: 'screenshot_after_login.png' });

    // Collect initial local storage
    const ls = await page.evaluate(() => Object.assign({}, window.localStorage));
    
    report += `## Local Storage\n`;
    report += `* access_token exists? ${!!ls.access_token}\n`;
    report += `* refresh_token exists? ${!!ls.refresh_token}\n`;
    if (ls.access_token) {
        const at = ls.access_token;
        report += `* access_token (first 20): ${at.substring(0, 20)}\n`;
        report += `* access_token (last 20): ${at.substring(at.length - 20)}\n`;
    }
    if (ls.refresh_token) {
        const rt = ls.refresh_token;
        report += `* refresh_token (first 20): ${rt.substring(0, 20)}\n`;
        report += `* refresh_token (last 20): ${rt.substring(rt.length - 20)}\n`;
    }
    report += `\n`;

    report += `## Network Requests\n\n`;
    // Filter relevant requests
    const adminRequests = networkRequests;

    report += `## Request Headers\n\n`;
    report += `## Response Bodies\n\n`;

    for (let req of adminRequests) {
        report += `### ${req.method} ${req.url}\n`;
        report += `* Status Code: ${req.response ? req.response.status : 'Pending'}\n`;
        report += `* Authorization: ${req.headers['authorization'] || 'None'}\n`;
        report += `* Origin: ${req.headers['origin'] || 'None'}\n`;
        report += `* Referer: ${req.headers['referer'] || 'None'}\n`;
        report += `* Host: ${req.headers['host'] || 'None'}\n\n`;

        const authHeader = req.headers['authorization'] || '';
        report += `**Token Verification:**\n`;
        report += `* Is Authorization header present? ${!!authHeader}\n`;
        report += `* Does it begin with Bearer? ${authHeader.startsWith('Bearer')}\n`;
        const tokenSent = authHeader.replace('Bearer ', '');
        report += `* Is access token identical to localStorage? ${tokenSent === ls.access_token}\n\n`;

        if (req.response) {
            report += `**Response:**\n`;
            report += `\`\`\`json\n${req.response.body}\n\`\`\`\n\n`;
        }
    }

    report += `## Token Comparison\n`;
    report += `Based on the requests, the Authorization token sent in the failed request is `;
    // Check the failed admin request
    const failedAdminReq = adminRequests.find(r => r.url.includes('/admin/') && r.response && r.response.status === 403);
    if (failedAdminReq) {
        const tokenSent = (failedAdminReq.headers['authorization'] || '').replace('Bearer ', '');
        report += `${tokenSent === ls.access_token ? 'identical' : 'different'} to the token stored in localStorage.\n\n`;
    } else {
        report += `N/A (No failed admin requests found or no requests to /admin/).\n\n`;
    }

    console.log("Testing refresh flow by reloading page...");
    // Clear network requests to watch refresh flow clearly
    networkRequests = [];
    await page.reload({ waitUntil: 'domcontentloaded' });
    await new Promise(r => setTimeout(r, 4000)); // wait for all requests

    report += `## Refresh Flow\n\n`;
    const refreshRequests = networkRequests.filter(r => r.url.includes('/auth/me') || r.url.includes('/auth/refresh') || r.url.includes('/admin/dashboard'));
    
    let flowStr = '';
    for (let r of refreshRequests) {
        flowStr += `${r.method} ${r.url} -> ${r.response ? r.response.status : '?'}\n`;
    }
    report += `\`\`\`text\n${flowStr}\n\`\`\`\n\n`;
    
    // Check what token /admin/dashboard used after refresh
    const dashboardReqAfterRefresh = refreshRequests.find(r => r.url.includes('/admin/dashboard'));
    if (dashboardReqAfterRefresh) {
        const tokenSent = (dashboardReqAfterRefresh.headers['authorization'] || '').replace('Bearer ', '');
        const newLs = await page.evaluate(() => window.localStorage.access_token);
        const oldToken = ls.access_token;
        if (tokenSent === newLs) {
            report += `After refresh completes, \`/admin/dashboard\` uses the **refreshed access token**.\n\n`;
        } else if (tokenSent === oldToken) {
            report += `After refresh completes, \`/admin/dashboard\` uses the **old access token**.\n\n`;
        } else {
            report += `After refresh completes, \`/admin/dashboard\` uses an unknown token.\n\n`;
        }
    } else {
        report += `Could not determine /admin/dashboard token usage after refresh.\n\n`;
    }

    report += `## Console Errors\n\n`;
    for (let err of consoleErrors) {
        report += `* ${err}\n`;
    }
    report += `\n`;

    const envApiUrl = await page.evaluate(() => {
        // Next.js usually injects process.env into some global if exposed, but if not we just guess
        // We can check the requests host
        return "Check Network Requests Host";
    });
    
    report += `## Root Cause Analysis\n\n`;
    report += `Based on the evidence:\n`;
    report += `1. **Token mismatch / Synchronization issue**: If the token sent to the backend differs from the localStorage token, this indicates a state desync in the frontend (e.g. using a stale token in memory/Axios interceptor, or Server Components not having access to localStorage token). [Check Token Comparison]\n`;
    report += `2. **Refresh Flow Race Condition**: If \`/admin/dashboard\` is fired *before* \`/auth/refresh\` completes, or with the old token. [Check Refresh Flow]\n`;
    report += `3. **CORS / Preflight**: If OPTIONS fails. [Check Network Errors]\n`;
    report += `4. **Missing Bearer prefix**: [Check Token Verification]\n\n`;

    report += `(The exact root cause will be identified by reviewing the above evidence.)\n`;

    fs.writeFileSync('RUNTIME_DEBUG_REPORT.md', report);
    console.log("Report generated at RUNTIME_DEBUG_REPORT.md");

    await browser.close();
})();
