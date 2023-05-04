import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-csz$do)us-&0)uyayoli+h316)$182rn1!jq_6f+)th)*arhh&'

DEBUG = True

AUTH_USER_MODEL = "account.Account"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.AllowAllUsersModelBackend" , 
    "account.backends.CaseInsensitiveModelBackend"
)

ALLOWED_HOSTS = ["*"]

DISABLE_DARK_MODE = True

INSTALLED_APPS = [
    # ----- my added apps  starts -------
    'personal.apps.PersonalConfig',
    'account.apps.AccountConfig',
    'friend.apps.FriendConfig' , 
    'public_chat.apps.PublicChatConfig' , 
    'chat.apps.ChatConfig' , 
    'notification.apps.NotificationConfig' , 
    'django_non_dark_admin',
    # ----- my added apps ends ----------
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize' ,    
    'channels' , 
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

ROOT_URLCONF = 'SocialMediaSite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR , "templates")],
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

WSGI_APPLICATION = 'SocialMediaSite.wsgi.application'
ASGI_APPLICATION = 'SocialMediaSite.routing.application'

if os.environ.get("MYSQL_PASSWORD") : 
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379)],
            },
        },
    }
else : 
    CHANNEL_LAYERS = {
        "default" : {
            "BACKEND" : "channels.layers.InMemoryChannelLayer" , 
        }
    }
if os.environ.get("MYSQL_PASSWORD") : 
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', 
            'NAME': 'socialmedia',                      
            'USER': 'root',                      
            'PASSWORD': os.environ.get("MYSQL_PASSWORD"),         
            'HOST': '127.0.0.1',                 
            'PORT': '3306',
        }
    }
else : 
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATICFILES_DIRS = [
    os.path.join(BASE_DIR , "static") ,
    os.path.join(BASE_DIR , "media") , 
]

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(BASE_DIR , "static_cdn") 
MEDIA_ROOT  = os.path.join(BASE_DIR , "media_cdn" )


TEMP = os.path.join(BASE_DIR , "media_cdn/temp") 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG : 
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    
DATA_UPLOAD_MAX_MEMORY_SIZE = 1_04_85_760  # 10 * 1024 * 1024  ( 10 MEGABYTES ) 

if DEBUG : 
    BASE_URL = "http://localhost:8000"
else : 
    BASE_URL = ""

# AWS_ACCESS_KEY_ID ="H7TEXYRQV5DU3IDTXPXC"
# AWS_SECRET_ACCESS_KEY ="6oFvNj9jnqTNvW7rD7GMxdZDQ1Q4Tij7ODaU3zJDM2A"
# AWS_STORAGE_BUCKET_NAME = "chat-app007"
# AWS_S3_ENDPOINT_URL = "https://nyc3.digitaloceanspaces.com"
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }
# AWS_LOCATION = "chat-app-static"


# TEMP = os.path.join(BASE_DIR, 'temp')
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'