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
    book_id = str(len(books) + 1)
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
        del books[book_id]
        # Remove transactions for this book
        for tx in list(transactions):
            if tx['book_id'] == book_id:
                transactions.remove(tx)
        return '', 204
    return 'Book not found', 404