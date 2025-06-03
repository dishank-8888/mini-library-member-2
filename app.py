
from flask import Flask, render_template, send_from_directory
import os
# --- User Management ---
@app.route('/users/<user_id>', methods=['GET', 'POST', 'DELETE'])
def manage_users():
    if request.method == 'GET':
        return jsonify(list(users.values()))
    elif request.method == 'POST':
        data = request.json
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error':'Name required'}), 400
        user_id = str(uuid.uuid4()) #generates unique uuid
        users[user_id] = {'id': user_id, 'name': name}
        return jsonify(users[user_id]), 201
    elif request.method == 'DELETE':
        user_id = request.args.get('id')
        if user_id in users:
            del users[user_id]
            # Remove user's borrowed books
            for tx in list(transactions):
                if tx['user_id'] == user_id:
                    transactions.remove(tx)
            return '', 204
        return 'User not found', 404
def delete_user(user_id):
    if user_id in users:

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'static/covers'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/covers/<filename>')
def cover_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
    from flask import request, jsonify, session

users = {}
books = {}
transactions = []

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'status':'error', 'message':'Name required'}), 400
    user = next((u for u in users.values() if u['name'].lower() == name.lower()), None)
    if not user:
        user_id = str(len(users) + 1)
        user = {'id': user_id, 'name': name}
        users[user_id] = user
    session['user_id'] = user['id']
    return jsonify({'status':'success', 'user': user})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'status':'success'})

@app.route('/session')
def check_session():
    user_id = session.get('user_id')
    if user_id and user_id in users:
        return jsonify({'logged_in':True, 'user':users[user_id]})
    return jsonify({'logged_in':False})
@app.route('/books')
def list_books():
    if 'user_id' not in session:
        return jsonify({'status':'error', 'message':'Login required'}), 401
    return jsonify({'books': list(books.value

@app.route('/books', methods=['GET'])
def manage_books():
    query = request.args.get('q', '').lower()
    avail = request.args.get('availability')
    result = []
    for book in books.values():
        matches = query in book['title'].lower() or query in book['author'].lower()
        if not query or matches:
            # Check availability

            is_borrowed = any(
                tx for tx in transactions
                if tx['book_id'] == book['id'] and tx['action']=='borrow' and
                not any(
                    t2 for t2 in transactions
                    if t2['book_id']==book['id'] and t2['action']=='return' and t2['date'] > tx['date']
                )
            )
           # Preprocess transactions once per request
            book_status = {}
            for tx in sorted(transactions, key=lambda x: x['date']):
                if tx['action'] in ('borrow', 'return'):
                 book_status[tx['book_id']] = (tx['action'] == 'borrow')

            is_borrowed = book_status.get(book['id'], False)

            book_copy = book.copy()
            book_copy['available'] = not is_borrowed
            if avail == 'available' and is_borrowed:
                continue
            if avail == 'borrowed' and not is_borrowed:
                continue
            if book['cover']:
                book_copy['cover_url'] = '/static/covers/' + book['cover']
            else:
                book_copy['cover_url'] = ''
            result.append(book_copy)
    return jsonify(result)
    @app.route('/books', methods=['POST'])
def manage_books():
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    if not title or not author:
        return jsonify({'error':'Title and author required'}), 400
    from uuid import uuid4
book_id = str(uuid4())

    cover = ''
    if 'cover' in request.files:
        file = request.files['cover']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{book_id}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            cover = filename
    books[book_id] = {'id': book_id, 'title': title, 'author': author, 'cover': cover}
    return jsonify(books[book_id]), 201
    @app.route('/books', methods=['DELETE'])
def manage_books():

    book_id = request.args.get('id')
    if book_id in books:
        # Delete cover image
        cover = books[book_id]['cover']
        if cover:
            try:
                os.remove(os.path.join(UPLOAD_FOLDER, cover))
            except Exception:
                pass
    elif request.method == 'DELETE':
    if not (book_id := request.args.get('id')):
        return jsonify({'error': 'Missing book ID'}), 400
        
    if book_id not in books:
        return jsonify({'error': 'Book not found'}), 404

    cover_path = os.path.join(UPLOAD_FOLDER, books[book_id]['cover'])
    if os.path.exists(cover_path):
        try:
            os.remove(cover_path)
        except OSError as e:
            app.logger.error(f"Failed to delete cover: {str(e)}")

        del books[book_id]
        # Remove transactions for this book
        for tx in list(transactions):
            if tx['book_id'] == book_id:
                transactions.remove(tx)
        return '', 204
    return 'Book not found', 404

from datetime import datetime

# --- Borrow/Return ---
@app.route('/transactions', methods=['GET', 'POST'])
def manage_transactions():
    if request.method == 'GET':
        return jsonify(transactions)
    elif request.method == 'POST':
        data = request.json
        action = data['action'] # 'borrow' or 'return'
        user_id = data['user_id']
        book_id = data['book_id']
        if user_id not in users or book_id not in books:
            return jsonify({'status':'error', 'message':'Invalid user or book'}), 400
        is_borrowed = any(
            tx for tx in transactions
            if tx['book_id'] == book_id and tx['action']=='borrow' and
            not any(
                t2 for t2 in transactions
                if t2['book_id']==book_id and t2['action']=='return' and t2['date'] > tx['date']
            )
        )
        if action == 'borrow':
            if is_borrowed:
                return jsonify({'status':'error', 'message':'Book already borrowed'}), 400
        elif action == 'return':
            if not is_borrowed:
                return jsonify({'status':'error', 'message':'Book is not borrowed'}), 400
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        transactions.append({
            'user_id': user_id,
            'user_name': users[user_id]['name'],
            'book_id': book_id,
            'book_title': books[book_id]['title'],
            'action': action,
            'date': date
        })
        return jsonify({'status': 'success'}), 201
    # --- User Borrowed Books ---
@app.route('/user_borrowed_books')
def user_borrowed_books():
    user_id = request.args.get('user_id')
    borrowed = []
    for tx in transactions:
        if tx['user_id'] == user_id and tx['action'] == 'borrow':
            # Check if not returned
            book_id = tx['book_id']
            returned = any(
                t2 for t2 in transactions
                if t2['book_id']==book_id and t2['user_id']==user_id and t2['action']=='return' and t2['date'] > tx['date']
            )
            if not returned:
                book = books[book_id].copy()
                if book['cover']:
                    book['cover_url'] = '/static/covers/' + book['cover']
                else:
                    book['cover_url'] = ''
                borrowed.append(book)
    return jsonify(borrowed)

