import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
	UPLOAD_FOLDER = '/app/static/images'
	LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	WTF_CSRF_SECRET_KEY='a secondary scret key'
	SQLALCHEMY_DATABASE_URI = os.environ.get('HEROKU_POSTGRESQL_ONYX_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
	#Setting up email config
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['trg1379@gmail.com']
	#Setting pagination limits - Currently disabled - need to reenable
	RECIPES_PER_PAGE = 50
	INGREDIENTS_PER_PAGE = 25
	USERS_PER_PAGE = 25
	COLLECTIONS_PER_PAGE = 25
	BOOKS_PER_PAGE = 10