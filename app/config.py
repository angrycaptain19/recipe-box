import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	#SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SECRET_KEY = 'you-will-never-guess'
	WTF_CSRF_SECRET_KEY='a secondary scret key'
	SQLALCHEMY_DATABASE_URI = os.environ.get('HEROKU_POSTGRESQL_WHITE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False