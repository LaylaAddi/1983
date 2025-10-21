import os
from pathlib import Path
from django.core.mail import send_mail


# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-fallback-secret-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '1983ls.com', 'www.1983ls.com', '.ngrok-free.dev', '.ngrok-free.app', '.ngrok.io']

# Database configuration


if os.environ.get('DATABASE_URL'):
    # Production (Render) database settings
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

    ALLOWED_HOSTS.extend(['.onrender.com'])
    
    # CSRF settings for Render
    CSRF_TRUSTED_ORIGINS = [
        'https://*.onrender.com',
    ]
else:
    # Development database settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'lawsuit_app',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'db',
            'PORT': '5432',
        }
    }

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
    'documents',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings (add these)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

# For development, you might want to allow all origins
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # In production, add your frontend domain
    CORS_ALLOWED_ORIGINS.extend([
        # Add your frontend URLs here, e.g.:
        # "https://your-frontend-domain.com",
    ])

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'  # Changed from CompressedManifestStaticFilesStorage

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mail.privateemail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'info@1983ls.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Section 1983 Generator <info@1983ls.com>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 10
PASSWORD_RESET_TIMEOUT = 3600  # Token valid for 1 hour

# Optional: Use console backend in development if you prefer
if DEBUG and os.environ.get('USE_CONSOLE_EMAIL', 'False').lower() == 'true':
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Additional production settings
if not DEBUG:
    # Security settings for production
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'


# Stripe Configuration
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Stripe Price IDs
STRIPE_PRICE_PAY_PER_DOC = 'price_1SHX4aIesUVMoyj1TqKzAnCo'
STRIPE_PRICE_UNLIMITED = 'price_1SHX7PIesUVMoyj1iUVOKsWN'

# Pricing
PRICE_PAY_PER_DOC = 149.00
PRICE_UNLIMITED = 499.00


# Site Configuration
SITE_NAME = 'Section 1983 Lawsuit Generator'
SUPPORT_EMAIL = 'info@1983ls.com'

# Site URL - can be overridden by environment variable
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000' if DEBUG else 'https://1983ls.com')