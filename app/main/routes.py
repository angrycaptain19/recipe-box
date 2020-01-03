from flask import render_template, Flask, redirect, url_for, flash, request, current_app, g, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from app import db, login
from app.models import User, Ingredients, Recipe2
from app.main.forms import RecipeForm, LoginForm, RegistrationForm, IngredientForm, RecipeSubmissionForm, SearchForm
from app.main import bp
from scrapertest import recipePull
import sys


# Defines allowed files for uploads
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@bp.route('/')
@bp.route('/index')
def index():
	page = request.args.get('page', 1, type=int)
	recipes = Recipe2.query.order_by(Recipe2.id.desc()).paginate(page, current_app.config['RECIPES_PER_PAGE'],False)
	next_url = url_for('main.discover', page=recipes.next_num) if recipes.has_next else None
	prev_url = url_for('main.discover', page=recipes.prev_num) if recipes.has_prev else None
	return render_template('discover.html', title='Discover', Recipes=recipes.items, next_url=next_url, prev_url=prev_url)

@bp.route('/recipes')
def discover():
	page = request.args.get('page', 1, type=int)
	recipes = Recipe2.query.order_by(Recipe2.id.desc()).paginate(page, current_app.config['RECIPES_PER_PAGE'],False)
	next_url = url_for('main.discover', page=recipes.next_num) if recipes.has_next else None
	prev_url = url_for('main.discover', page=recipes.prev_num) if recipes.has_prev else None
	return render_template('discover.html', title='Discover', Recipes=recipes.items, next_url=next_url, prev_url=prev_url)

@bp.route('/my_recipes')
@login_required
def my_recipes():
	recipes = Recipe2.query.filter_by(user_id=current_user.id)
	return render_template('my_recipes.html', title='My Recipes', Recipes=recipes)

@bp.route('/recipeSubmission', methods=['GET','POST'])
@login_required
def recipeSubmission():
	form = RecipeSubmissionForm()
	if form.validate_on_submit():
		inputurl = form.recipeurl.data
		recipePull(inputurl)
		return redirect(url_for('main.index'))	
	return render_template('recipeSubmission.html', form=form)
 
#_________________________________________________
# User facing recipe sections		
	

@bp.route('/create_recipe', methods=['GET','POST'])
@login_required
def create_recipe():
	return render_template('create_recipe.html', title='Create a Recipe')

#___________________________________________________

# Login section:
# The next 


@bp.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first_or_404()
		password_check = check_password_hash(user.password_hash, form.password.data)
		if user is None or not password_check:
			flash('Invalid username or password')
			return redirect(url_for('main.login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != "":
			next_page = url_for('main.index')
# If a user is an admin first redirect them to the ingredients manager. This is currently the basis for a more complete admin view
		if user.isAdmin is True:
			next_page = url_for('main.admin')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		password_hash = generate_password_hash(form.password.data)
		user = User(username=form.username.data, email=form.email.data, password_hash=password_hash)
		#user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('main.login'))
	return render_template('register.html', title='Register', form=form)

#Ingredients page is currently the full admin view. It allows an admin to create ingredients and view current ingredients

@bp.route('/admin', methods=['GET'])
@login_required
def admin():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	return render_template('admin.html')

@bp.route('/admin/ingredients', methods=['GET','POST'])
@login_required
def manage_ingredients():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	ingredients = Ingredients.query.paginate(page, current_app.config['INGREDIENTS_PER_PAGE'],False)
	next_url = url_for('main.manage_ingredients', page=ingredients.next_num) if ingredients.has_next else None
	prev_url = url_for('main.manage_ingredients', page=ingredients.prev_num) if ingredients.has_prev else None
	return render_template('manage_ingredients.html', Ingredients = ingredients.items, next_url = next_url, prev_url = prev_url)


@bp.route('/admin/recipes', methods=['GET','POST'])
@login_required
def manage_recipes():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	recipes = Recipe2.query.paginate(page, current_app.config['RECIPES_PER_PAGE'],False)
	book_list = books.query.all()
	next_url = url_for('main.manage_recipes', page=recipes.next_num) if recipes.has_next else None
	prev_url = url_for('main.manage_recipes', page=recipes.prev_num) if recipes.has_prev else None
	return render_template('manage_recipes.html', Recipes = recipes.items, books=book_list, next_url = next_url, prev_url = prev_url)

@bp.route('/admin/create/recipe', methods=['GET','POST'])
@login_required
def admin_create_recipe():
	if current_user.isAdmin is not True:
		return('Unable to access')
		return redirect(url_for('main.index'))
	return render_template('admin_create_recipe.html')

@bp.route('/admin/submit_recipe', methods=['GET','POST'])
def submit_recipe():
	if request.method == 'POST':
		#pull in all individual form responses. First create the Recipe record w/ no ingredients or steps
		recipeName = request.form['recipeName']
		mealType = request.form['mealType']
		Image = request.form['Image']
		prepTime = request.form['prepTime']
		if prepTime is None or "" or " ":
			prepTime = 0.
		cookTime = request.form['cookTime']
		if cookTime is None or "" or " ":
			cookTime = 0.
		recipeCheck = Recipe2.query.filter_by(recipeName=recipeName).first()
		if recipeCheck is not None:
			flash('A recipe with this name already exists. Please choose a new name for your recipe')
			return redirect(url_for('main.admin_create_recipe'))
		recipe = Recipe(recipeName=recipeName, mealType=mealType, Image=Image, prepTime=prepTime, cookTime=cookTime)
		db.session.add(recipe)
#		Pull in ingredient information, then query for the recipe we just created to get ID and create the recipeIngredients record for these ingredients
		ingredientNames = request.form.getlist('ingredientName')
		ingredientMeasurements = request.form.getlist('ingredientMeasurement')
		ingredientAmounts = request.form.getlist('ingredientAmount')
		recipeRecord = Recipe2.query.filter_by(recipeName=recipeName).first()
		recipeRecordID = recipeRecord.id
#		Iterate over all the ingredients in the recipe Form
		i = 0
		for ingredientName in ingredientNames:
#		Check if this ingredient already exists in the ingredient table and if not create an ingredient record for that ingredient
			ingredient = Ingredients.query.filter_by(ingredientName=ingredientName).first()	
			if ingredient is None:
				newIngredient = Ingredients(ingredientName=ingredientName)
				db.session.add(newIngredient)
				ingredient = Ingredients.query.filter_by(ingredientName=ingredientName).first()
			db.session.add(recipeIngredient)
			i + 1
		recipeSteps = request.form.getlist('recipeStep')
		j=0
		for recipeStep in recipeSteps:
			j=j+1
			step = Recipe_Steps(recipe_id=recipeRecordID, stepNumber=j, directions=recipeStep)
			db.session.add(step)
		db.session.commit()
		return  redirect(url_for('main.admin'))

@bp.route('/admin/users')
@login_required
def manage_users():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	users = User.query.paginate(page, current_app.config['USERS_PER_PAGE'],False)
	next_url = url_for('main.manage_users', page=users.next_num) if users.has_next else None
	prev_url = url_for('main.manage_users', page=users.prev_num) if users.has_prev else None
	return render_template('manage_users.html', Users = users.items, next_url = next_url, prev_url = prev_url)

#___________________________________________________
# Search route
@bp.route('/search', methods = ['GET','POST'])
def search():
	term = request.form['search']
	print(term)
	search_recipes = Recipe2.query.filter(Recipe2.recipeName.contains(term)).limit(3).all()
	print(search_recipes)
	return render_template('search.html', title=('Search Results'), term=term, recipes=search_recipes)




