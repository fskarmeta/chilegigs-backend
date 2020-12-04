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
