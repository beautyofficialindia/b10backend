"""
Test-specific settings that override DATABASE to use SQLite.
Use with: python manage.py test --settings=core.settings_test

This avoids relying on the external Supabase instance during automated tests,
which can cause transient OperationalError failures when the connection drops.
"""
from core.settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Silence emails during testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
