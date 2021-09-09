import os

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '-05sgp9!deq=q1nltm@^^2cc+v29i(tyybv3v2t77qi66czazj'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'crispy_forms',
    'django_countries',


    'core'

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'project_dj_ecart.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_files')]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
    }
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_REDIRECT_URL = '/'

# Django crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

PUBLISHABLE_KEY = "pk_test_51JXKanSA0MyYYyHhlUzJ594Bo8MYQtQgXoOpaKxOuHJjOA9EU8XnalxSl5rjhVvmhWlOjLcTe65uHtXUiJWddQrm00LuTLdaoP"
SECRET_KEY = "sk_test_51JXKanSA0MyYYyHh3tBvEZX6KxyYF3Timl8QZHcqFgyK7oxYkRQc29R0oSpMPOZsVW7Ia0LKd4eVCt4wZCicA2mB00AmoWyyq1"

# STRIPE_API_KEY = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"  # from just django
STRIPE_API_KEY = "sk_test_51JXKanSA0MyYYyHh3tBvEZX6KxyYF3Timl8QZHcqFgyK7oxYkRQc29R0oSpMPOZsVW7Ia0LKd4eVCt4wZCicA2mB00AmoWyyq1"

# To fix ConnectionRefusedError at /accounts/password/reset/
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sahiljmi102@gmail.com'
EMAIL_HOST_PASSWORD = 'Sahilraza@1029534'
