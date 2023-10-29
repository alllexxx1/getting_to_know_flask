def validate(data):
	errors = {}
	if len(data['nickname']) < 3:
		errors['nickname'] = f'{data["nickname"]} is less than 3 characters'
	if len(data['nickname']) > 11:
		errors['nickname'] = f'{data["nickname"]} is greater than 11 characters'
	return errors


def w_validate(word):
	errors = {}
	if not word['word'].isascii():
		errors['word'] = 'You should use only latin characters'
	if any(char.isdigit() for char in word['word']):
		errors['word'] = 'You shouldn\'t use numbers'
	if not word['definition'].isascii():
		errors['definition'] = 'You should utilize only english definitions for the sake of faster progress'
	return errors


def i_validate(data):
	errors = {}
	return errors
