@app.route('/books', methods=['GET'])
def manage_books():
    query = request.args.get('q', '').lower()
    avail = request.args.get('availability')
    result = []
    for book in books.values():
        matches = query in book['title'].lower() or query in book['author'].lower()
        if not query or matches:
            # Check availability
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