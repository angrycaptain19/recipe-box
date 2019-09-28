from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, backref
from app.search import add_to_index, remove_from_index, query_index

# class SearchableMixin(object):
#     @classmethod
#     def search(cls, expression, page, per_page):
#         ids, total = query_index(cls.__tablename__, expression, page, per_page)
#         if total == 0:
#             return cls.query.filter_by(id=0), 0
#         when = []
#         for i in range(len(ids)):
#             when.append((ids[i], i))
#         return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total

#     @classmethod
#     def before_commit(cls, session):
#         session._changes = {
#             'add': list(session.new),
#             'update': list(session.dirty),
#             'delete': list(session.deleted)
#         }

#     @classmethod
#     def after_commit(cls, session):
#         for obj in session._changes['add']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['update']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['delete']:
#             if isinstance(obj, SearchableMixin):
#                 remove_from_index(obj.__tablename__, obj)
#         session._changes = None

#     @classmethod
#     def reindex(cls):
#         for obj in cls.query:
#             add_to_index(cls.__tablename__, obj)

# db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
# db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(128), index=True, unique=True)
	email = db.Column(db.String(256), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	isAdmin = db.Column(db.Boolean)
	createdCollections = db.relationship('collections', backref="created_by", lazy="dynamic")
	createdRecipes = db.relationship('Recipe', backref="created by", lazy="dynamic")
	savedRecipes = db.relationship('savedrecipes', backref="saved by", lazy="dynamic")
#	followed_Collections = db.relationship('collections', secondary='collectionFollowers', primaryjoin=('collection_followers.c.follower_id' == id), secondaryjoin=('collection_followers.c.collection_id' == id), backref=db.backref('collectionFollowers', lazy="dynamic"), lazy="dynamic")
	followed_Collections = db.relationship('collections', secondary="collectionFollowers")
#	followed_books = db.relationship('books', secondary='bookFollowers', primaryjoin=('book_followers.c.follower_id' == id), secondaryjoin=('book_followers.c.book_id' == id), backref=db.backref('bookFollowers', lazy="dynamic"), lazy="dynamic")
	followed_Books = db.relationship('books', secondary="bookFollowers")


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
	# __searchable__ = ['Ingredients']
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
	Ingredients = db.relationship('recipe_ingredients', backref="Recipe", lazy="dynamic")
	collections = db.relationship('collections', secondary="recipeCollections")
	savedRecipes = db.relationship('savedrecipes', backref="saved recipe", lazy="dynamic")

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
	standardUnitAmount = db.Column(db.String)
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
	ingredientName = db.Column(db.String)
	ingredientAmount = db.Column(db.String)
	ingredientUnit = db.Column(db.String)

	recipe = db.relationship(Recipe, backref=backref("recipe_ingredients",cascade="all, delete-orphan"))
	ingredients = db.relationship(Ingredients, backref=backref("recipe_ingredients",cascade="all, delete-orphan"))

	def __repr__(self):
		return '<Recipe Ingredients {}'.format(self.recipe_id)

#Collections are used to create sets of recipes that can be unified around any set of criteria. Collections are user defined and have a creator. Eventually want to make it so you can have public and private collections
class collections(db.Model):
	# __searchable__ = ['collection_name', 'description', 'recipes']
	id = db.Column(db.Integer, primary_key=True)
	collection_name = db.Column(db.String(256))
	description = db.Column(db.String)
	created_by_2 = db.Column(db.Integer, db.ForeignKey('user.id'))
	photoURL = db.Column(db.String)
	recipes = db.relationship('Recipe', secondary='recipeCollections')
	followers = db.relationship('User', secondary='collectionFollowers')

	def __repr__(self):
		return '<Collections{}'.format(self.collection_name)

class recipe_collections(db.Model):
	__tablename__ = "recipeCollections"
	id = db.Column(db.Integer, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
#	recipe = db.relationship(Recipe, backref=backref("recipe_collections", cascade="all, delete-orphan"))
	collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))
#	collection = db.relationship(collections, backref=backref("recipe_collections", cascade="all, delete-orphan"))

class collection_followers(db.Model):
	__tablename__ = "collectionFollowers"
	id = db.Column(db.Integer, primary_key=True)
	collection_follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	follower = db.relationship(User, backref=backref("collection_followers", cascade="all, delete-orphan"))
	collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'))
#	collection = db.relationship(collections, backref=backref("collection_followers", cascade="all, delete-orphan"))

class books(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	book_name = db.Column(db.String(256))
	author = db.Column(db.String(256))
	photoURL = db.Column(db.String)
	recipes = db.relationship('Recipe', secondary='recipeBooks')
	followers = db.relationship('User', secondary='bookFollowers')

class recipe_books(db.Model):
	__tablename__ = "recipeBooks"
	id = db.Column(db.Integer, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
#	recipe = db.relationship(Recipe, backref=backref("recipe_books", cascade="all, delete-orphan"))
	book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
#	book = db.relationship(books, backref=backref("recipe_books", cascade="all, delete-orphan"))

class book_followers(db.Model):
	__tablename__ = "bookFollowers"
	id = db.Column(db.Integer, primary_key=True)
	book_follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	follower = db.relationship(User, backref=backref("book_followers", cascade="all, delete-orphan"))
	book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
#	book = db.relationship(books, backref=backref("book_followers", cascade="all, delete-orphan"))

class savedrecipes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	saved_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	saved_recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))



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
	Instructions = db.relationship('Recipe_Steps2', backref="Recipe", lazy="dynamic")
#	Ingredients = []	
	Ingredients = db.relationship('recipe_ingredients2', backref="Recipe", lazy="dynamic")

	def __repr__(self):
		return '<Recipe {}>'.format(self.recipeName)


class recipe_ingredients2(db.Model):
	__tablename__ = "recipeIngredients2"
	id = db.Column(db.Integer, primary_key=True)
	recipe2_id = db.Column(db.Integer, db.ForeignKey('recipe2.id'))
	ingredient = db.Column(db.String)

class Recipe_Steps2(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipe2.id'))
	directions = db.Column(db.String)	

class collections2(db.Model):
	# __searchable__ = ['collection_name', 'description', 'recipes']
	id = db.Column(db.Integer, primary_key=True)
	collection_name = db.Column(db.String(256))
	description = db.Column(db.String)
	created_by_2 = db.Column(db.Integer, db.ForeignKey('user.id'))
	photoURL = db.Column(db.String)
