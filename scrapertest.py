import requests
import urllib.request
import time
import json
from bs4 import BeautifulSoup
from flask import render_template, Flask, redirect, url_for, flash, request, current_app, g, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from app import db, login
from app.models import Recipe, User, Ingredients, recipe_ingredients, Recipe_Steps, books, collections, collection_followers, book_followers, recipe_books, recipe_collections, savedrecipes, Recipe2, recipe_ingredients2, Recipe_Steps2

def recipePull(input_url):

	url = input_url
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')


	#breaks out the single script. Assaumes that the script type is going to be the same across all sites (needs some confirmation)
	try:
		one_script_tag = soup.findAll('script',{'type' : 'application/ld+json'})[0]
	except: 
		one_script_tag = "invalid"
		flash('Invalid recipe')

	try: 
		meta_title = soup.findAll('meta', {'property':'og:title'})[0]
	except:
		meta_title = "invalid"

	print(meta_title)
	try:
		meta_image = soup.findAll('meta', {'property':'og:image'})[0]
	except:
		meta_image = "invalid"

	print(meta_image)

	#print(one_script_tag)

	if (one_script_tag != "invalid"):	
		script_content = one_script_tag.contents[0]
		parsed_script = json.loads(script_content)
	if (meta_title != "invalid"):
		meta_title_content = meta_title['content']
	if (meta_image != "invalid"):
		meta_image_content = meta_image['content']

# pull in image 
	if (meta_image != "invalid"):
		try:
			image_url= meta_image_content
		except:
			try:
				image_url = parsed_script['image']
				if type(image_url) != str:
					image_url = image_url[0]
			except:
				try:
					image_url = parsed_script['image'][0]
				except:
					image_url = ""
	else:					
		try:
			image_url = parsed_script['image']
			if type(image_url) != str:
				image_url = image_url[0]
		except:
			try:
				image_url = parsed_script['image'][0]
			except:
				image_url = ""
#____________________________________________________

#pull in recipe name 
	if(meta_title != "invalid"):
		try:
			name = meta_title_content
		except:
			try:
				name = parsed_script['name']
			except:
				name = ""
	else:
		try:
			name = parsed_script['name']
		except:
			name = ""

#___________________________________________________

	try:
		author = parsed_script['author']['name']
	except:
		author = ""

	try: 
		description = parsed_script['description']
	except:
		description = ""

	try:
		keywords = parsed_script['keywords']
	except:
		keywords = ""

	try:
		ratingCount = parsed_script['aggregateRating']['ratingCount']
	except:
		ratingCount = None

	try:
		ratingValue = parsed_script['aggregateRating']['ratingValue']
	except:
		ratingValue = None

	try:
		recipeCategory = parsed_script['recipeCategory']
	except:
		recipeCategory = ""

	try:
		recipeCuisine = parsed_script['recipeCuisine']
	except:
		recipeCuisine = ""

	try:
		recipeIngredients = parsed_script['recipeIngredient']
	except:
		recipeIngredients = ""

	try:
		recipeInstructions = parsed_script['recipeInstructions']
	except:
		recipeInstructions = ""


	try:
		recipeYield = parsed_script['recipeYield']
	except:
		recipeYield = ""


	#"author":{"@type":"Person","name":"Justine Pattison"}

	recipe = Recipe2(recipeURL=url, recipeName=name, ratingCount=ratingCount, ratingValue=ratingValue, image_url=image_url, description=description, author=author, keywords=keywords, recipeCategory=recipeCategory, recipeCuisine=recipeCuisine,recipeYield=recipeYield, user_id=current_user.id)
	db.session.add(recipe)

	recipeRecord = Recipe2.query.filter_by(recipeURL=url).first()
	recipeRecordID = recipeRecord.id
	i = 0
	for ingredient in recipeIngredients:
		if type(ingredient) == str:
			recipeIngredient = recipe_ingredients2(recipe2_id=recipeRecordID, ingredient=ingredient)
			db.session.add(recipeIngredient)
		else:
			print("invalid ingredient")
	for recipeInstruction in recipeInstructions:
		if type(recipeInstruction) == str:
			instruction = Recipe_Steps2(recipe_id=recipeRecordID, directions=recipeInstruction)
			db.session.add(instruction)
		else:
			print("invalid step")
	db.session.commit()  


	# print("image url " + image_url)
	# print("author " + author)
	# print("description " + description)
	# print("keywords " + keywords)
	# print("ratingCount " + str(ratingCount))
	# print("ratingValue " + str(ratingValue))
	# print("Recipe name" + name)
	# print("recipe Category " + recipeCategory)
	# print("recipe Cuisine " + recipeCuisine)
	# print("recipe instructions: ")  
	# print(recipeInstructions)
	# print("recipe Ingredients: ")
	# print(recipeIngredients)
	# print("recipe Yield " + recipeYield)

