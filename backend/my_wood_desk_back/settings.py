# Librería de python para manejar rutas más fácilmente
from pathlib import Path

from django.contrib.messages import constants as message_constants

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Especifica la ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
# Templates directory
TEMPLATES_DIR = BASE_DIR / 'my_wood_desk_back' / 'templates'

# Static files configuration
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'my_wood_desk_back' / 'static',
]

# Media files configuration
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# SECURITY WARNING: keep the secret key used in production secret!
# Clave secreta para encriptación y seguridad de contraseñas
SECRET_KEY = 'django-insecure-1l70%&(lz!qow#wg^3bg_&-yt8dyh45gi+r8^eipm8-vk#)1%g'

# SECURITY WARNING: don't run with debug turned on in production!
# El modo debug para cuando activo el servidor de django en desarrollo
DEBUG = True

# Array de urls permitidas para acceder al servidor
ALLOWED_HOSTS = []

# Aplicaciones base instaladas en el proyecto
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de terceros
    'django_extensions',  # Extensiones de Django
    'crispy_forms',
    'crispy_bootstrap5',
    # 'rest_framework',  # API REST framework
    # 'corsheaders',  # Soporte para CORS (React)

    # Aplicaciones del proyecto
    'profiles',
    'posts',
    'notifications',
    'study',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_wood_desk_back.urls'

# Muestra donde se encuentran las plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Context processors personalizados
                'my_wood_desk_back.context_processors.navigation_counts',
                'my_wood_desk_back.context_processors.site_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'my_wood_desk_back.wsgi.application'

# Database
# Configuración de la base de datos, en este caso SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
# Caracteristicas de validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
# Idioma y zona horaria del proyecto
LANGUAGE_CODE = 'es-ES'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
# Aquí se configuran los archivos estáticos
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}
