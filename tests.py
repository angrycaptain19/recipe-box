from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import Recipe

class RecipeModelCase(unittest.TestCase)
	def setUp(self):
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all
