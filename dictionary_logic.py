from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
from word_validator import w_validate
import json


WORDS_PER_PAGE = 5


def create_form():
	word = []
	errors = []

	return render_template(
	'words/new.html',
	word=word,
	errors=errors
		)

def process_form():
	word = request.form.to_dict()
	ru = word.get('ru', '')
	ru = ru.encode('utf-8').decode('unicode-escape')
	errors = w_validate(word)
	if errors:
		return render_template(
			'words/new.html',
			word=word,
			errors=errors
		), 422

	try:
		with open('words.json') as file:
			words = json.load(file)
	except FileNotFoundError:
		words = []
	except json.decoder.JSONDecodeError:
		words = []
	words.append(word)
	with open('words.json', 'w') as file:
		file.write(json.dumps(words, indent=2))
	flash(f'A word {word["en"]} has been added to your short-term memory. Try your best to move it to your long-term one')
	return redirect(
		url_for('get_words'), code=302
	) 


def map_words():
	try:
		with open('words.json') as file:
			words = json.load(file)
	except FileNotFoundError:
		words = ''
	except json.decoder.JSONDecodeError:
		words = ''
	
	page = request.args.get('page', 1, int)
	start = WORDS_PER_PAGE * (page - 1)
	finish = start + WORDS_PER_PAGE
	current_words = words
	if len(words) > 4:
		current_words = words[start:finish]
	total_pages = (len(words) + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE

	message = get_flashed_messages(with_categories=True)

	return render_template(
	'words/index.html',
	words=words,
	page=page,
	total_pages=total_pages,
	message=message
	)

