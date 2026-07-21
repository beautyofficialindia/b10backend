import os
import django
import sys
from datetime import timedelta
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.analytics.services.export_service import AnalyticsExportService
from django.utils import timezone

context = {
    "start_date": timezone.now() - timedelta(days=30),
    "end_date": timezone.now(),
    "period": "30d"
}
modules = ['overview', 'leads', 'crm', 'chat', 'knowledge', 'users']
for mod in modules:
    try:
        print(f"Testing module: {mod}")
        AnalyticsExportService.generate_csv(mod, context)
        print(f"Module {mod} success")
    except Exception as e:
        print(f"Exception caught for {mod}:")
        traceback.print_exc()
