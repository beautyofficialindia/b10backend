from datetime import timedelta
from django.utils import timezone
from .constants import HealthStatus

def safe_division(numerator, denominator, precision=2):
    if not denominator:
        return 0.0
    return round(float(numerator) / float(denominator), precision)

def calculate_percentage(numerator, denominator, precision=2):
    return round(safe_division(numerator, denominator, precision + 2) * 100, precision)

def calculate_growth(current_val, previous_val):
    diff = current_val - previous_val
    pct = calculate_percentage(diff, previous_val) if previous_val > 0 else (100.0 if current_val > 0 else 0.0)
    return {
        "difference": diff,
        "growth_percentage": pct
    }

def build_metric(title, value, previous_value=None, enabled=True):
    metric = {
        "title": title,
        "value": value,
        "enabled": enabled
    }
    if previous_value is not None:
        metric["previous_value"] = previous_value
        growth = calculate_growth(value, previous_value)
        metric.update(growth)
    return metric

def build_health(module_name, status, enabled, tracking_enabled, message=""):
    return {
        "module": module_name,
        "status": status,
        "enabled": enabled,
        "tracking_enabled": tracking_enabled,
        "message": message
    }

def build_trend(title, labels, values):
    return {
        "title": title,
        "labels": labels,
        "values": values
    }

def get_period_dates(start_date, end_date):
    if not start_date or not end_date:
        return None, None
    period_duration = end_date - start_date
    prev_end = start_date
    prev_start = prev_end - period_duration
    return prev_start, prev_end

def format_labels(trends, date_field='date', count_field='count', format_str='%b %d'):
    labels = []
    values = []
    for t in trends:
        if t.get(date_field):
            labels.append(t[date_field].strftime(format_str))
            values.append(t[count_field])
    return labels, values
