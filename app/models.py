from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref
from app.search import add_to_index, remove_from_index, query_index

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), index=True, unique=True)
	email = db.Column(db.String(256), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	isAdmin = db.Column(db.Boolean)
	createdRecipes = db.relationship('Recipe2', backref="created by", lazy="dynamic")


	def __repr__(self):
		return '<User {}'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Ingredients is a table that has all possible ingredients including a base unit of measurement for that recipes ingredients
class Ingredients(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ingredientName = db.Column(db.String, index=True, unique=True)
	ingredientType = db.Column(db.String(128))
	# Defines a standard unit (eg gram) that the ingredient is measured in
	measurementUnit = db.Column(db.String(128))
	# Defines the standard amount of the standard unit - eg 100 grams
	standardUnitAmount = db.Column(db.String)
#	recipes = []
#
	def __repr__(self):
		return '<Ingredient {}'.format(self.ingredientName)

class Recipe2(db.Model):
	# __searchable__ = ['Ingredients']
	id = db.Column(db.Integer, primary_key=True)
	recipeURL = db.Column(db.String, index=True)
	recipeName = db.Column(db.String(128), index=True)
	ratingCount = db.Column(db.Integer)
	ratingValue = db.Column(db.Float)
	image_url = db.Column(db.String(256))
	description = db.Column(db.String)
	author = db.Column(db.String)
	keywords = db.Column(db.String)
	recipeCategory = db.Column(db.String)
	recipeCuisine = db.Column(db.String)
	recipeYield = db.Column(db.String)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	Instructions = db.relationship('Recipe_Steps2', backref="Recipe", lazy="dynamic")
#	Ingredients = []	
#	Ingredients = db.relationship('recipe_ingredients2', backref="Recipe", lazy="dynamic")

	def __repr__(self):
		return '<Recipe {}>'.format(self.recipeName)


# class recipe_ingredients2(db.Model):
# 	__tablename__ = "recipeIngredients2"
# 	id = db.Column(db.Integer, primary_key=True)
# 	recipe2_id = db.Column(db.Integer, db.ForeignKey('recipe2.id'))
# 	ingredient = db.Column(db.String)

# class Recipe_Steps2(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe2.id'))
# 	directions = db.Column(db.String)	

class collections2(db.Model):
	# __searchable__ = ['collection_name', 'description', 'recipes']
	id = db.Column(db.Integer, primary_key=True)
	collection_name = db.Column(db.String(256))
	description = db.Column(db.String)
	created_by_2 = db.Column(db.Integer, db.ForeignKey('user.id'))
	photoURL = db.Column(db.String)
