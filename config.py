from os import environ
from dotenv import load_dotenv
load_dotenv()

class Base:
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(
        environ.get('DBUSER'), 
        environ.get('DBPASS'), 
        environ.get('DBHOST'), 
        environ.get('DBPORT'),
        environ.get('DBNAME')
    )
    JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    SECRET_KEY = ''
    MAIL_SERVER  = environ.get('MAIL_SERVER')
    MAIL_PORT = environ.get('MAIL_PORT')
    # MAIL_USE_SSL  = bool(environ.get('MAIL_USE_SSL'))
    MAIL_USE_TLS = bool(environ.get('MAIL_USE_TLS'))
    MAIL_DEBUG  = bool(environ.get('MAIL_DEBUG'))
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER  = environ.get('MAIL_USERNAME')