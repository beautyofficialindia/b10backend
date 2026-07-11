const fs = require('fs');
const path = require('path');

const pages = [
  { file: 'leads/page.tsx', perm: 'leads.view_lead' },
  { file: 'crm/page.tsx', perm: 'crm.view_leadactivity' },
  { file: 'analytics/page.tsx', perm: 'analytics.view_analyticsevent' },
  { file: 'users/page.tsx', perm: 'auth.view_user' },
  { file: 'roles/page.tsx', perm: 'auth.view_group' },
  { file: 'knowledge/page.tsx', perm: 'knowledge_base.view_kbentry' },
  { file: 'settings/page.tsx', perm: 'settings_management.view_setting' },
];

const basePath = 'c:/workflow/b10backend/adminfrontend/app/(dashboard)';

pages.forEach(({ file, perm }) => {
  const filePath = path.join(basePath, file);
  if (!fs.existsSync(filePath)) {
    console.log('Not found: ' + filePath);
    return;
  }
  let content = fs.readFileSync(filePath, 'utf8');
  
  if (content.includes('<PermissionGuard')) {
    console.log('Already guarded: ' + filePath);
    return;
  }

  // Import PermissionGuard
  if (!content.includes('PermissionGuard')) {
    content = content.replace(/(import .* from '@\/components\/layout';)/, "$1\nimport { PermissionGuard } from '@/features/auth';");
  }

  // Wrap return ( <PageContainer> ... </PageContainer> )
  content = content.replace(/<PageContainer(.*?)>/g, `<PermissionGuard permissions={['${perm}']}>\n    <PageContainer$1>`);
  content = content.replace(/<\/PageContainer>/g, '<\/PageContainer>\n    <\/PermissionGuard>');

  fs.writeFileSync(filePath, content);
  console.log('Guarded: ' + filePath);
});
