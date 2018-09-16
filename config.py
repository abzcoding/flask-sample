DEBUG = True
SECRET_KEY = 'secret'
SQLALCHEMY_DATABASE_URI = 'sqlite:///api.sqlite'
USE_TOKEN_AUTH = False
USE_RATE_LIMITS = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
BROKER_URL = 'redis://localhost:6379/0'
