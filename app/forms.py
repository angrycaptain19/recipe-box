from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, PasswordField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Recipe2, User, Ingredients

class RecipeForm(FlaskForm):
	recipeName = StringField('Recipe Name', validators=[DataRequired()])
	Ingredients = StringField('Ingredients')
	Instructions = StringField('Instructions')
	Image = StringField('Image URL')
	prepTime = StringField('Preperation Time (minutes)')
	cookTime = StringField('Cooking Time (minutes)')
	Rating = FloatField('Recipe Rating (1-5 scale)')
	mainIngredient = StringField('Recipe\'s Primary Ingredient')
	mealType = StringField('Type of Recipe')
	submit = SubmitField('Create Recipe')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address')

class IngredientForm(FlaskForm):
	ingredientName = StringField('Ingredient Name', validators=[DataRequired()])
	ingredientType = StringField('Ingredient Type', validators=[DataRequired()])
	measurementUnit = StringField('Standard Mesurement Unit', validators=[DataRequired()])
	standardUnitAmount = StringField('Standard Measurement Amount', validators=[DataRequired()])
	submit = SubmitField('Create Ingredient')


