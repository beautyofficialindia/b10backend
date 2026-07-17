import csv
from io import StringIO
from django.http import HttpResponse
from .overview_service import OverviewAnalyticsService
from .lead_analytics_service import LeadAnalyticsService
from .crm_analytics_service import CrmAnalyticsService
from .chat_analytics_service import ChatAnalyticsService
from .knowledge_analytics_service import KnowledgeAnalyticsService
from .user_analytics_service import UserAnalyticsService

class AnalyticsExportService:
    
    @staticmethod
    def _flatten_metrics(metrics_dict):
        # Convert {"total_leads": {"title": "Total Leads", "value": 150}} to row
        rows = []
        for key, data in metrics_dict.items():
            if isinstance(data, dict) and 'title' in data and 'value' in data:
                rows.append([data['title'], data['value']])
        return rows
        
    @staticmethod
    def _flatten_trend(trend_dict):
        # Convert {"title": "Lead Growth", "labels": [...], "values": [...]} to rows
        rows = []
        if trend_dict and 'labels' in trend_dict and 'values' in trend_dict:
            title = trend_dict.get('title', 'Trend')
            labels = trend_dict['labels']
            values = trend_dict['values']
            for idx, label in enumerate(labels):
                val = values[idx] if idx < len(values) else ""
                rows.append([title, label, val])
        return rows
        
    @staticmethod
    def _flatten_insights(insights_list):
        rows = []
        for insight in insights_list:
            if isinstance(insight, dict):
                rows.append([insight.get('title', ''), insight.get('value', '')])
        return rows

    @staticmethod
    def generate_csv(module, context):
        output = StringIO()
        writer = csv.writer(output)
        
        service_map = {
            'overview': OverviewAnalyticsService,
            'leads': LeadAnalyticsService,
            'crm': CrmAnalyticsService,
            'chat': ChatAnalyticsService,
            'knowledge': KnowledgeAnalyticsService,
            'users': UserAnalyticsService,
        }
        
        service = service_map.get(module)
        if not service:
            return None
            
        data = service.build_response(context)
        
        writer.writerow(["Analytics Export", module.upper()])
        writer.writerow([])
        
        for section, section_data in data.items():
            if not isinstance(section_data, dict) or not section_data.get('enabled'):
                continue
                
            writer.writerow([f"--- {section.replace('_', ' ').title()} ---"])
            
            content = section_data.get('data')
            if isinstance(content, dict):
                if 'labels' in content and 'values' in content:
                    # It's a trend
                    writer.writerow(["Metric", "Label/Date", "Value"])
                    writer.writerows(AnalyticsExportService._flatten_trend(content))
                else:
                    # It's executive metrics
                    writer.writerow(["Metric", "Value"])
                    writer.writerows(AnalyticsExportService._flatten_metrics(content))
            elif isinstance(content, list):
                # Insights
                writer.writerow(["Insight", "Value"])
                writer.writerows(AnalyticsExportService._flatten_insights(content))
                
            writer.writerow([])
            
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="analytics_{module}.csv"'
        return response
