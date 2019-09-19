from flask import render_template, Flask, redirect, url_for, flash, request, current_app, g, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from config import Config
from app import db, login
from app.models import Recipe, User, Ingredients, recipe_ingredients, Recipe_Steps, books, collections, collection_followers, book_followers, recipe_books, recipe_collections 
from app.main.forms import RecipeForm, LoginForm, RegistrationForm, IngredientForm, collectionForm, BookForm, SearchForm
from app.main import bp
import sys


# Defines allowed files for uploads
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@bp.route('/')
@bp.route('/index')
def index():
	recipeList = Recipe.query.limit(3).all()
	bookList = books.query.limit(3).all()
	collectionList = collections.query.limit(3).all()
	return render_template('home.html', Recipes = recipeList, Books=bookList, Collections=collectionList)

@bp.route('/discover')
def discover():
	page = request.args.get('page', 1, type=int)
	recipes = Recipe.query.order_by(Recipe.timestamp.desc()).paginate(page, current_app.config['RECIPES_PER_PAGE'],False)
	next_url = url_for('main.discover', page=recipes.next_num) if recipes.has_next else None
	prev_url = url_for('main.discover', page=recipes.prev_num) if recipes.has_prev else None
	return render_template('discover.html', title='Discover', Recipes=recipes.items, next_url=next_url, prev_url=prev_url)

#_________________________________________________
# User facing recipe sections		

@bp.route('/recipe/<id>')
def recipe(id):
	recipe = Recipe.query.filter_by(id=id).first_or_404()
	user_collections = []
	if current_user.is_anonymous != True:
		user_collections = collections.query.filter_by(created_by=current_user.id).all()
	return render_template('recipe.html', recipe=recipe, user_collections=user_collections)
	

@bp.route('/create_recipe', methods=['GET','POST'])
@login_required
def create_recipe():
	return render_template('create_recipe.html', title='Create a Recipe')

@bp.route('/submit_recipe', methods=['GET','POST'])
def user_submit_recipe():
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
		recipeCheck = Recipe.query.filter_by(recipeName=recipeName).first()
		if recipeCheck is not None:
			flash('A recipe with this name already exists. Please choose a new name for your recipe')
			return redirect(url_for('main.admin_create_recipe'))
		# file = request.files['file']
		# if file and allowed_file(file.filename):
		# 	filename = secure_filename(file.filename)
		# 	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		recipe = Recipe(recipeName=recipeName, mealType=mealType, Image=Image, prepTime=prepTime, cookTime=cookTime)
		db.session.add(recipe)
#		Pull in ingredient information, then query for the recipe we just created to get ID and create the recipeIngredients record for these ingredients
		ingredientNames = request.form.getlist('ingredientName')
		ingredientMeasurements = request.form.getlist('ingredientMeasurement')
		ingredientAmounts = request.form.getlist('ingredientAmount')
		print("Names:")
		print(ingredientNames)
		print("Measurements") 
		print(ingredientMeasurements)
		print("Amounts")
		print(ingredientAmounts)
		print(ingredientMeasurements[1])
		print(ingredientAmounts[1])
		recipeRecord = Recipe.query.filter_by(recipeName=recipeName).first()
		recipeRecordID = recipeRecord.id
#		Iterate over all the ingredients in the recipe Form
		i = 0
		for ingredientName in ingredientNames:
			print(i)
#		Check if this ingredient already exists in the ingredient table and if not create an ingredient record for that ingredient
			ingredient = Ingredients.query.filter_by(ingredientName=ingredientName).first()	
			if ingredient is None:
				newIngredient = Ingredients(ingredientName=ingredientName)
				db.session.add(newIngredient)
				ingredient = Ingredients.query.filter_by(ingredientName=ingredientName).first()
			recipeIngredient = recipe_ingredients(recipe_id=recipeRecordID, ingredient_id=ingredient.id, ingredientName=ingredientName, ingredientAmount=ingredientAmounts[i], ingredientUnit=ingredientMeasurements[i])
			db.session.add(recipeIngredient)
			i = i + 1
		recipeSteps = request.form.getlist('recipeStep')
		j=0
		for recipeStep in recipeSteps:
			j=j+1
			step = Recipe_Steps(recipe_id=recipeRecordID, stepNumber=j, directions=recipeStep)
			db.session.add(step)
		db.session.commit()
		return  redirect(url_for('main.index'))

#__________________________________________________
# User facing collections section

@bp.route('/collections')
def collection_list():
	page = request.args.get('page', 1, type=int)
	collection_list = collections.query.paginate(page, current_app.config['COLLECTIONS_PER_PAGE'],False)
	next_url = url_for('main.collection_list', page=collection_list.next_num) if collection_list.has_next else None
	prev_url = url_for('main.collection_list', page=collection_list.prev_num) if collection_list.has_prev else None
	return render_template('collection_list.html', collections = collection_list.items, next_url = next_url, prev_url = prev_url)


@bp.route('/collection/<id>')
def collection(id):
	collection = collections.query.filter_by(id=id).first_or_404()
	collection_id = collection.id
	Recipe_collections = recipe_collections.query.filter_by(collection_id=collection_id)
#	recipe_ids = Recipe_collections.recipe_id
#	recipes = recipe.query.filter_by(id=recipe_ids)
	return render_template('collection.html', collection=collection)#, recipes = recipes)

@bp.route('/create-collection', methods=['GET','POST'])
@login_required
def create_collection():
	form = collectionForm()
	if form.validate_on_submit():
		collection = collections(collection_name=form.collectionName.data, description=form.collectionDescription.data, photoURL=form.photoURL.data)
		db.session.add(collection)
		db.session.commit()
		return redirect(url_for('main.collection_list'))
	return render_template('create_collection.html', form=form)

@bp.route('/add-to-collection/<current_collection>/<current_recipe>')
@login_required
def add_to_collection(current_collection, current_recipe):
	collection = collections.query.filter_by(id=current_collection).first_or_404()
	recipe = Recipe.query.filter_by(id=current_recipe).first()
	collection.recipes.append(recipe)
	db.session.commit()
	flash('Recipe added to collection!')
	return redirect(url_for('main.recipe', id=current_recipe))

#_________________________________________
#User facing books section

@bp.route('/books')
def book_list():
	page = request.args.get('page', 1, type=int)
	book_list = books.query.paginate(page, current_app.config['BOOKS_PER_PAGE'],False)
	next_url = url_for('main.book_list', page=book_list.next_num) if book_list.has_next else None
	prev_url = url_for('main.book_list', page=book_list.prev_num) if book_list.has_prev else None
	return render_template('book_list.html', books=book_list.items, next_url = next_url, prev_url=prev_url)

@bp.route('/book/<id>')
def book(id):
	book = books.query.filter_by(id=id).first_or_404()
	return render_template('book.html', book=book)

#Admin facing book creation

@bp.route('/admin/manage_books')
@login_required
def manage_books():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	book_list = books.query.paginate(page, current_app.config['BOOKS_PER_PAGE'],False)
	next_url = url_for('main.book_list', page=book_list.next_num) if book_list.has_next else None
	prev_url = url_for('main.book_list', page=book_list.prev_num) if book_list.has_prev else None
	return render_template('manage_books.html', books=book_list.items, next_url = next_url, prev_url=prev_url)	

@bp.route('/admin/create-book', methods=['GET','POST'])
@login_required
def create_book():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	form = BookForm()
	if form.validate_on_submit():
		book = books(book_name=form.book_name.data, author=form.author.data, photoURL=form.photoURL.data)
		db.session.add(book)
		db.session.commit()
		return redirect(url_for('main.manage_books'))
	return render_template('create_book.html', form=form)	

#___________________________________________________

# Login section:
# The next 


@bp.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
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
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
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

@bp.route('/admin/create/ingredient', methods=['GET','POST'])
@login_required
def create_ingredient():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	form = IngredientForm()
	if form.validate_on_submit():
		ingredient = Ingredients(ingredientName=form.ingredientName.data, ingredientType=form.ingredientType.data, measurementUnit=form.measurementUnit.data, standardUnitAmount=form.standardUnitAmount.data)
		db.session.add(ingredient)
		db.session.commit()
		return redirect(url_for('main.manage_ingredients'))
	return render_template('create_ingredient.html', title='Create Ingredient', form=form)

@bp.route('/admin/recipes', methods=['GET','POST'])
@login_required
def manage_recipes():
	if current_user.isAdmin is not True:
		flash('Unable to access')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	recipes = Recipe.query.paginate(page, current_app.config['RECIPES_PER_PAGE'],False)
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
		recipeCheck = Recipe.query.filter_by(recipeName=recipeName).first()
		if recipeCheck is not None:
			flash('A recipe with this name already exists. Please choose a new name for your recipe')
			return redirect(url_for('main.admin_create_recipe'))
		recipe = Recipe(recipeName=recipeName, mealType=mealType, Image=Image, prepTime=prepTime, cookTime=cookTime)
		db.session.add(recipe)
#		Pull in ingredient information, then query for the recipe we just created to get ID and create the recipeIngredients record for these ingredients
		ingredientNames = request.form.getlist('ingredientName')
		ingredientMeasurements = request.form.getlist('ingredientMeasurement')
		ingredientAmounts = request.form.getlist('ingredientAmount')
		recipeRecord = Recipe.query.filter_by(recipeName=recipeName).first()
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

@bp.route('/admin/add-to-book/<current_book>/<current_recipe>')
@login_required
def add_to_book(current_book, current_recipe):
	book = books.query.filter_by(id=current_book).first_or_404()
	recipe = Recipe.query.filter_by(id=current_recipe).first()
	book.recipes.append(recipe)
	db.session.commit()
	flash('Recipe added to book!')
	return redirect(url_for('main.manage_recipes'))

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
	search_recipes = Recipe.query.filter(Recipe.recipeName.contains(term)).limit(3).all()
	search_collections = collections.query.filter(collections.collection_name.contains(term)).limit(3).all()
	search_books = books.query.filter(books.book_name.contains(term)).limit(3).all()
	search_term = term
	return render_template('search.html', title=('Search Results'), term=term, recipes=search_recipes, collections = search_collections, books = search_books)


# Image Sending Route
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



