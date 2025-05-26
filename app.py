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