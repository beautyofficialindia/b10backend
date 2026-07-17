from datetime import datetime, timedelta, time
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.analytics.constants import AnalyticsPeriods

class AnalyticsFilterService:
    @staticmethod
    def parse_period(period_str):
        if not period_str or period_str not in AnalyticsPeriods.ALLOWED_PERIODS:
            return AnalyticsPeriods.DEFAULT_PERIOD
        return period_str

    @staticmethod
    def parse_dates(start_date_str, end_date_str):
        start_date, end_date = None, None
        try:
            if start_date_str:
                parsed = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_date = timezone.make_aware(datetime.combine(parsed.date(), time.min))
            if end_date_str:
                parsed = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = timezone.make_aware(datetime.combine(parsed.date(), time.max))
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        return start_date, end_date

    @staticmethod
    def validate_period(period, start_date, end_date):
        if period == AnalyticsPeriods.CUSTOM:
            if not start_date or not end_date:
                raise ValidationError("start_date and end_date are required for custom period.")
            # Use .date() for day-level boundary comparison — works for both date and aware datetime
            start_d = start_date.date() if hasattr(start_date, 'date') else start_date
            end_d = end_date.date() if hasattr(end_date, 'date') else end_date
            if start_d > end_d:
                raise ValidationError("start_date cannot be greater than end_date.")
            if (end_d - start_d).days > AnalyticsPeriods.CUSTOM_PERIOD_MAX_DAYS:
                raise ValidationError(f"Custom period cannot exceed {AnalyticsPeriods.CUSTOM_PERIOD_MAX_DAYS} days.")
        return True

    @staticmethod
    def _day_start(d):
        """Return a timezone-aware datetime at the start of the given date."""
        return timezone.make_aware(datetime.combine(d, time.min))

    @staticmethod
    def _day_end(d):
        """Return a timezone-aware datetime at the end of the given date (inclusive)."""
        return timezone.make_aware(datetime.combine(d, time.max))

    @staticmethod
    def get_date_range(period, start_date=None, end_date=None):
        now = timezone.now()
        today = now.date()

        if period == AnalyticsPeriods.TODAY:
            return AnalyticsFilterService._day_start(today), AnalyticsFilterService._day_end(today)
        elif period == AnalyticsPeriods.SEVEN_DAYS:
            return AnalyticsFilterService._day_start(today - timedelta(days=7)), AnalyticsFilterService._day_end(today)
        elif period == AnalyticsPeriods.THIRTY_DAYS:
            return AnalyticsFilterService._day_start(today - timedelta(days=30)), AnalyticsFilterService._day_end(today)
        elif period == AnalyticsPeriods.NINETY_DAYS:
            return AnalyticsFilterService._day_start(today - timedelta(days=90)), AnalyticsFilterService._day_end(today)
        elif period == AnalyticsPeriods.CUSTOM:
            return start_date, end_date

        return AnalyticsFilterService._day_start(today - timedelta(days=30)), AnalyticsFilterService._day_end(today)

    @staticmethod
    def get_previous_period(start_date, end_date):
        if not start_date or not end_date:
            return None, None
        period_duration = end_date - start_date
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - period_duration
        return prev_start, prev_end

    @staticmethod
    def build_filter_context(request):
        period_str = request.query_params.get('period')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        period = AnalyticsFilterService.parse_period(period_str)
        start_date, end_date = AnalyticsFilterService.parse_dates(start_date_str, end_date_str)
        
        AnalyticsFilterService.validate_period(period, start_date, end_date)
        
        calculated_start, calculated_end = AnalyticsFilterService.get_date_range(period, start_date, end_date)
        prev_start, prev_end = AnalyticsFilterService.get_previous_period(calculated_start, calculated_end)
        
        return {
            "period": period,
            "start_date": calculated_start,
            "end_date": calculated_end,
            "previous_start_date": prev_start,
            "previous_end_date": prev_end
        }
