export const kpiData = [
  { title: 'Total Leads', value: '1,284', change: '+14.2% from last month', changeType: 'positive' as const },
  { title: 'Qualified Leads', value: '342', change: '+8.1% from last month', changeType: 'positive' as const },
  { title: 'Active Opportunities', value: '89', change: '-2.4% from last month', changeType: 'negative' as const },
  { title: 'Conversion Rate', value: '26.7%', change: '+3.1% from last month', changeType: 'positive' as const },
];

export const leadsOverTime = [
  { month: 'Jan', leads: 65 },
  { month: 'Feb', leads: 78 },
  { month: 'Mar', leads: 92 },
  { month: 'Apr', leads: 85 },
  { month: 'May', leads: 110 },
  { month: 'Jun', leads: 134 },
  { month: 'Jul', leads: 148 },
];

export const leadSources = [
  { source: 'Website', count: 45 },
  { source: 'Chatbot', count: 32 },
  { source: 'Referral', count: 18 },
  { source: 'Social', count: 12 },
  { source: 'Direct', count: 8 },
];

export const recentActivity = [
  { id: 1, action: 'New lead captured', description: 'Rahul Sharma from TechCorp', time: '2 minutes ago', type: 'lead' as const },
  { id: 2, action: 'Lead qualified', description: 'Priya Patel - Mobile App Project', time: '15 minutes ago', type: 'qualified' as const },
  { id: 3, action: 'Knowledge article published', description: 'Getting Started Guide updated', time: '1 hour ago', type: 'knowledge' as const },
  { id: 4, action: 'User activated', description: 'sales_user@b10.com', time: '2 hours ago', type: 'user' as const },
  { id: 5, action: 'New lead captured', description: 'Amit Verma - E-commerce Website', time: '3 hours ago', type: 'lead' as const },
  { id: 6, action: 'Settings updated', description: 'AI model changed to GPT-4o', time: '5 hours ago', type: 'settings' as const },
];

export const recentLeads = [
  { id: 1, name: 'Rahul Sharma', email: 'rahul@techcorp.in', company: 'TechCorp', status: 'gathering', project_type: 'Web Application', created: '2 min ago' },
  { id: 2, name: 'Priya Patel', email: 'priya@innovate.io', company: 'Innovate Labs', status: 'qualified', project_type: 'Mobile App', created: '15 min ago' },
  { id: 3, name: 'Amit Verma', email: 'amit@shop.co', company: 'ShopCo', status: 'gathering', project_type: 'E-commerce', created: '3 hrs ago' },
  { id: 4, name: 'Sneha Gupta', email: 'sneha@fintech.com', company: 'FinTech Solutions', status: 'qualified', project_type: 'AI/ML', created: '5 hrs ago' },
  { id: 5, name: 'Vikram Singh', email: 'vikram@logix.in', company: 'Logix Systems', status: 'gathering', project_type: 'Custom Software', created: '1 day ago' },
];
