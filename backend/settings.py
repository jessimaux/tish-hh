import os
from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__file__))
MEDIADIR = os.path.join(BASEDIR, 'media/')
MEDIAURL = '/media/'

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

DB_ENGINE = os.getenv('DB_ENGINE')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

EMAIL_USERNAME=os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD=os.getenv('EMAIL_PASSWORD')
EMAIL_FROM=os.getenv('EMAIL_FROM')
EMAIL_PORT=os.getenv('EMAIL_PORT')
EMAIL_SERVER=os.getenv('EMAIL_SERVER')

JWT_VERIFICATION_SECRET_KEY = os.getenv('JWT_VERIFICATION_SECRET_KEY')
JWT_RETRIEVE_PASSWORD_SECRET_KEY = os.getenv('JWT_RETRIEVE_PASSWORD_SECRET_KEY')