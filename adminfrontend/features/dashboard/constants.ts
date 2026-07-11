// The frontend consumes these permission strings. The backend is responsible for granting them to users.
export const WIDGET_REGISTRY = {
  kpiCards: {
    permissions: ['analytics.view_analyticsevent'],
  },
  funnelChart: {
    permissions: ['analytics.view_analyticsevent'],
  },
  timelineChart: {
    permissions: ['analytics.view_analyticsevent'],
  },
  recentLeads: {
    permissions: ['leads.view_lead'],
  },
  quickStats: {
    permissions: ['analytics.view_analyticsevent'],
  },
  // Pending Backend Implementation:
  systemStatus: {
    permissions: ['core.view_systemhealth'], // Placeholder backend permission
  },
  recentActivities: {
    permissions: ['audit.view_auditlog'], // Placeholder backend permission
  },
} as const;
