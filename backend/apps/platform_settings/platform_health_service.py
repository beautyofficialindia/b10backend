from django.utils import timezone
from apps.platform_settings.services import SettingsService
from apps.crm.models import LeadFollowUp
from apps.knowledge_base.models import KnowledgeEntry
from django.contrib.auth import get_user_model
from apps.platform_settings.models import PlatformSetting

class PlatformHealthService:
    @classmethod
    def get_system_alerts(cls):
        alerts = {
            "critical": [],
            "warning": [],
            "info": [],
            "is_healthy": True
        }

        try:
            if PlatformSetting.objects.count() == 0:
                alerts["critical"].append({"message": "Platform Settings have not been initialized."})
            
            ai_enabled = SettingsService.get_setting("GENERAL", "ENABLE_AI_CHATBOT")
            email_enabled = SettingsService.get_setting("GENERAL", "ENABLE_EMAIL_NOTIFICATIONS")
            kb_enabled = SettingsService.get_setting("GENERAL", "ENABLE_KNOWLEDGE_BASE")
            crm_enabled = SettingsService.get_setting("GENERAL", "ENABLE_CRM")
            maintenance_mode = SettingsService.get_setting("GENERAL", "MAINTENANCE_MODE")
            auto_qual = SettingsService.get_setting("CRM", "AUTO_QUALIFICATION_ENABLED")

            if ai_enabled:
                if not SettingsService.get_setting("AI", "OPENROUTER_API_KEY"):
                    alerts["critical"].append({"message": "AI enabled but OpenRouter API key missing."})
                if not SettingsService.get_setting("AI", "DEFAULT_AI_MODEL"):
                    alerts["critical"].append({"message": "AI enabled but default model missing."})

            if email_enabled:
                if not SettingsService.get_setting("FEATURES", "SMTP_HOST"):
                    alerts["critical"].append({"message": "Email notifications enabled but SMTP configuration missing."})
                    
            if maintenance_mode:
                alerts["info"].append({"message": "Maintenance mode is active."})

            if crm_enabled:
                User = get_user_model()
                crm_users = User.objects.filter(is_active=True).count()
                if crm_users == 0:
                    alerts["warning"].append({"message": "CRM enabled but no active users exist."})

                overdue_followups = LeadFollowUp.objects.filter(
                    status="pending", 
                    scheduled_at__lt=timezone.now()
                ).count()
                if overdue_followups > 25:
                    alerts["warning"].append({"message": f"More than 25 overdue followups exist ({overdue_followups})."})
                
                if auto_qual:
                    threshold = SettingsService.get_setting("CRM", "LEAD_SCORE_THRESHOLD")
                    if threshold is None or threshold <= 0 or threshold > 100:
                        alerts["warning"].append({"message": "Lead qualification enabled but threshold value is invalid."})

            if kb_enabled:
                published_count = KnowledgeEntry.objects.filter(status="published").count()
                if published_count == 0:
                    alerts["warning"].append({"message": "Knowledge Base enabled but contains zero published entries."})
                
                draft_count = KnowledgeEntry.objects.filter(status="draft").count()
                if draft_count > 0:
                    alerts["info"].append({"message": f"Knowledge Base contains {draft_count} draft articles."})

        except Exception as e:
            alerts["critical"].append({"message": f"Settings module corrupted or unavailable: {str(e)}"})
            
        alerts["is_healthy"] = len(alerts["critical"]) == 0 and len(alerts["warning"]) == 0
        return alerts

