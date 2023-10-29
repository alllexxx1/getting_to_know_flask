from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
    make_response,
    session)
from validator import validate, w_validate, i_validate
# from dotenv import load_dotenv
import json
import os

# load_dotenv()
app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.secret_key = os.environ.get('SECRET_KEY')
app.secret_key = 'secret_key'

NAMES = ['Mike', 'Mishel', 'Adel', 'Keks', 'Kamila']
ID = 0
GUEST_PER_PAGE = 5
WORDS_PER_PAGE = 5


@app.errorhandler(404)
def not_found(error):
    return 'Stop looking for non-existent pages!', 404


@app.route('/', methods=['GET', 'POST'])
def greet():
    if request.method == 'GET':
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'greet.html',
            messages=messages
        )
    if request.method == 'POST':
        user = request.form.to_dict()
        user['password'] = '000'
        session['users'] = user
        flash('You are logged in. Push "logout" button to log out', 'success')
        return redirect(url_for('users'))


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out. '
          'Sign in to access the "users" page', 'success')
    return redirect(url_for('greet'))


@app.get('/users')
def users():
    term = request.args.get('term', '')
    users = NAMES
    if term:
        users = list(filter(lambda x: term.lower() in x.lower(), users))
    messages = get_flashed_messages(with_categories=True)

    emails = session.get('users')
    return render_template(
        'users/index.html',
        users=users,
        search=term,
        messages=messages,
        emails=emails
    )


@app.route('/course/<id>')
def courses(id):
    return f'Course ID is {id}'


@app.get('/guests')
def guests_get():
    try:
        with open('guests.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = ''
    except json.decoder.JSONDecodeError:
        data = ''
    if data:
        data = sorted(data, key=lambda x: x['nickname'].lower())

    page = request.args.get('page', 1, int)
    start = GUEST_PER_PAGE * page - GUEST_PER_PAGE
    finish = start + GUEST_PER_PAGE
    current_guests = data
    if len(data) > 4:
        current_guests = data[start:finish]
    total_pages = (len(data) + GUEST_PER_PAGE - 1) // GUEST_PER_PAGE
    prev_url = url_for('guests_get', page=page - 1) if page > 1 else None
    next_url = url_for('guests_get', page=page + 1) \
        if page < total_pages else None

    return render_template(
        'guests/index.html',
        current_guests=current_guests,
        page=page,
        total_pages=total_pages,
        prev_url=prev_url,
        next_url=next_url
    )


@app.post('/guests')
def guests_post():
    guest = request.form.to_dict()
    global ID
    ID += 1
    guest['id'] = ID
    errors = validate(guest)
    if errors:
        return render_template(
            'guests/new.html',
            guest=guest,
            errors=errors
        )
    try:
        with open('guests.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    except json.decoder.JSONDecodeError:
        data = []
    data.append(guest)
    with open('guests.json', 'w') as f:
        f.write(json.dumps(data))
    flash('User was added successfully', 'success')
    return redirect(
        url_for('get_guest', name=guest['nickname']), code=302
    )


@app.route('/guests/new')
def guests_new():
    guest = {'id': '',
             'nickname': '',
             'email': ''}
    errors = {}

    return render_template(
        'guests/new.html',
        guest=guest,
        errors=errors
    )


@app.route('/guests/<name>')
def get_guest(name):
    with open('guests.json') as f:
        guests = json.load(f)
    filtered_guests = filter(lambda guest: guest['nickname'] == name, guests)
    guest = next(filtered_guests, None)

    if guest is None:
        return 'Ooops', 404

    message = get_flashed_messages(with_categories=True)
    return render_template(
        'guests/show.html',
        guest=guest,
        message=message
    )


@app.get('/words/')
def get_words():
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
    if len(current_words) > 4:
        current_words = words[start:finish]
    total_pages = (len(words) + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE

    messages = get_flashed_messages(with_categories=True)

    term = request.args.get('term', '')
    if term:
        words = list(filter(
            lambda word: term.lower() in word['word'].lower(), words))
    else:
        words = ''

    return render_template(
        'words/index.html',
        current_words=current_words,
        words=words,
        search=term,
        page=page,
        total_pages=total_pages,
        messages=messages
    )


@app.route('/words/new')
def new_word():
    word = {}
    errors = {}

    return render_template(
        'words/new.html',
        word=word,
        errors=errors
    )


@app.post('/words')
def post_words():
    word = request.form.to_dict()
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
    flash(
        f'A word {word["word"]} has been added to your short-term memory. '
        f'Try your best to move it to your long-term one', 'success')

    return redirect(
        url_for('get_words'), code=302
    )


@app.route('/words/<slug>')
def get_word(slug):
    try:
        with open('words.json') as file:
            words = json.load(file)
    except FileNotFoundError:
        words = ''
    except json.decoder.JSONDecodeError:
        words = ''
    filtered_words = filter(lambda word: word['word'] == slug, words)
    word = next(filtered_words, None)

    if word is None:
        return f'There is no word "{slug}" in your dictionary yet', 404

    return render_template(
        'words/show.html',
        word=word
    )


@app.route('/words/<slug>/translation')
def get_translation(slug):
    with open('words.json') as file:
        words = json.load(file)
    filtered_words = filter(lambda word: word['word'] == slug, words)
    word = next(filtered_words, None)

    if word is None:
        return f'There is no word "{slug}" in your dictionary yet', 404

    return render_template(
        'words/show_translation.html',
        word=word
    )


# @app.route('/words/<slug>/edit')
# def edit_word(slug):
#     try:
#         with open('words.json') as file:
#             words = json.load(file)
#     except FileNotFoundError:
#         words = ''
#     except json.decoder.JSONDecodeError:
#         words = ''
#     filtered_words = filter(lambda word: word['word'] == slug, words)
#     word = next(filtered_words, None)
#     if word is None:
#         return f'There is no word "{slug}" in your dictionary yet', 404
#
#     errors = []
#     return render_template(
#         'words/edit.html',
#         word=word,
#         errors=errors
#     )
#
#
# @app.route('/words/<slug>/patch', methods=['POST'])
# def patch_word(slug):
#     with open('words.json') as file:
#         words = json.load(file)
#     word_id = [index for index, word in
#                enumerate(words) if word['word'] == slug]
#     word_id = next(iter(word_id))
#     filtered_words = filter(lambda word: word['word'] == slug, words)
#     word = next(filtered_words, None)
#     data = request.form.to_dict()
#     errors = w_validate(data)
#     if errors:
#         return render_template(
#             'words/edit.html',
#             word=word,
#             errors=errors
#         ), 422
#     word['word'] = data['word']
#     word['translation'] = data['translation']
#     words.insert(word_id, words.pop(word_id))
#     with open('words.json', 'w') as file:
#         file.write(json.dumps(words, indent=2))
#     flash(
#         'The word has been updated', 'success')
#
#     return redirect(
#         url_for('get_words'), code=302
#     )


@app.route('/words/<slug>/edit', methods=['GET', 'POST'])
def patch_word(slug):
    with open('words.json') as file:
        words = json.load(file)
    filtered_words = filter(lambda word: word['word'] == slug, words)
    word = next(filtered_words, None)
    errors = {}

    if request.method == 'GET':
        return render_template(
            'words/edit.html',
            word=word,
            errors=errors
        )

    if request.method == 'POST':
        data = request.form.to_dict()
        errors = w_validate(data)
        if errors:
            return render_template(
                'words/edit.html',
                word=word,
                errors=errors
            ), 422
        word['word'] = data['word']
        word['translation'] = data['translation']
        word_id = [index for index, word in
                   enumerate(words) if word['word'] == slug]
        word_id = next(iter(word_id))
        words.insert(word_id, words.pop(word_id))
        with open('words.json', 'w') as file:
            file.write(json.dumps(words, indent=2))
        flash(
            'The word has been updated', 'success')

        return redirect(
            url_for('get_words'), code=302
        )


@app.route('/words/<slug>/delete', methods=['POST'])
def delete_word(slug):
    with open('words.json') as file:
        words = json.load(file)
    word_id = [index for index, word in
               enumerate(words) if word['word'] == slug]
    word_id = next(iter(word_id))
    words.pop(word_id)
    with open('words.json', 'w') as file:
        file.write(json.dumps(words, indent=2))
    flash(
        f'The word {slug} has been deleted', 'success')

    return redirect(
        url_for('get_words'), code=302
    )


@app.get('/items')
def get_items():
    items = request.cookies.get('items')
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'items/index.html',
        messages=messages,
        items=items
    )


@app.post('/items')
def items_post():
    item = request.form.to_dict()
    errors = i_validate(item)
    if errors:
        return render_template(
            'items/new.html',
            item=item,
            errors=errors
        )
    items = json.loads(request.cookies.get('items', json.dumps([])))
    items.append(item)
    encoded_items = json.dumps(items)

    response = make_response(redirect(url_for('get_items')))
    # This is a valid option too
    # response = redirect(url_for('get_items'))
    response.set_cookie('items', encoded_items, max_age=10)
    flash('Item was added successfully', 'success')
    return response


@app.route('/items/new')
def items_new():
    item = {
        'name': '',
        'cost': ''
    }
    errors = {

    }

    return render_template(
        'items/new.html',
        item=item,
        errors=errors
    )


@app.route('/items/clean', methods=['POST'])
def items_clean():
    response = redirect(url_for('get_items'))
    response.delete_cookie('items')
    return response
