from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), index=True, unique=True)
	email = db.Column(db.String(256), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	isAdmin = db.Column(db.Boolean)
	createdRecipes = db.relationship('Recipe', backref="created by", lazy="dynamic")

	def __repr__(self):
		return '<User {}'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Recipe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	recipeName = db.Column(db.String(128), index=True)
	prepTime = db.Column(db.Float)
	cookTime = db.Column(db.Float)
	Rating = db.Column(db.Float)
	Image = db.Column(db.String(256))
	mainIngredient = db.Column(db.String(64))
	mealType = db.Column(db.String(64))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	Instructions = db.relationship('Recipe_Steps', backref="Recipe", lazy="dynamic")
#	Ingredients = []	
	Ingredients = db.relationship('Ingredients', secondary="recipeIngredients")


	def __repr__(self):
		return '<Recipe {}>'.format(self.recipeName)


# Ingredients is a table that has all possible ingredients including a base unit of measurement for that recipes ingredients
class Ingredients(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ingredientName = db.Column(db.String, index=True, unique=True)
	ingredientType = db.Column(db.String(128))
	# Defines a standard unit (eg gram) that the ingredient is measured in
	measurementUnit = db.Column(db.String(128))
	# Defines the standard amount of the standard unit - eg 100 grams
	standardUnitAmount = db.Column(db.Integer)
#	recipes = []
	recipes = db.relationship('Recipe', secondary='recipeIngredients')	

	def __repr__(self):
		return '<Ingredient {}'.format(self.ingredientName)


class Recipe_Steps(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
	stepNumber = db.Column(db.Integer)
	directions = db.Column(db.String)

	def __repr__(self):
		return '<Recipe Steps {}'.format(self.recipe_id)

# Links together a recipe and a set of ingredients 

class recipe_ingredients(db.Model):
	__tablename__ = "recipeIngredients"
	id = db.Column(db.Integer, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
	ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'))
	ingredientAmount = db.Column(db.Float)
	ingredientUnit = db.Column(db.String)

	recipe = db.relationship(Recipe, backref=backref("recipe_ingredients",cascade="all, delete-orphan"))
	ingredients = db.relationship(Ingredients, backref=backref("recipe_ingredients",cascade="all, delete-orphan"))

	def __repr__(self):
		return '<Recipe Ingredients {}'.format(self.recipe_id)


