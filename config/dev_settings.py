from .base_settings import *

# DEBUG
SITE_URL = ""
# END DEBUG
ALLOWED_HOSTS = ['*']


SESSION_COOKIE_SECURE = False 
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Mail settings
EMAIL_BACKEND = 'django.core.mail.backends.console.ConsoleBackend'

ADMIN_EMAIL = "psajaev@gmail.com"

# django-debug-toolbar
INSTALLED_APPS += ('debug_toolbar',)

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}
# end django-debug-toolbar

# Your local stuff: Below this line define 3rd party libary settings

SECRET_KEY = '787+h%v*7d$(g&qs#azmb!8=8_&o==o=%b_==bi%g=1a5@6*+v'