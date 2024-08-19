from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'

db = SQLAlchemy(app)

class Books(db.Model):
    bookID = db.Column(db.String(250), primary_key=True, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    authors = db.Column(db.String(250))
    average_rating = db.Column(db.String(250))
    isbn = db.Column(db.String(250))
    isbn13 = db.Column(db.String(250))
    language_code = db.Column(db.String(250))
    num_pages = db.Column(db.String(250))
    ratings_count = db.Column(db.String(250))
    text_reviews_count = db.Column(db.String(250))
    publication_date = db.Column(db.String(250))
    publisher = db.Column(db.String(250))
    no_of_copies_total = db.Column(db.Integer)
    no_of_copies_current = db.Column(db.Integer)
    # borrowed_by = db.relationship('Members', backref='owner')

@app.route('/')
def index():
    books = Books.query.all()
    return render_template('index.html', books=books)

@app.route('/add', methods=['POST'])
def add_book():
    bookID = request.form['bookID']
    title = request.form['title']
    authors = request.form['authors']
    average_rating = request.form['average_rating']
    isbn = request.form['isbn']
    isbn13 = request.form['isbn13']
    language_code = request.form['language_code']
    num_pages = request.form['num_pages']
    ratings_count = request.form['ratings_count']
    text_reviews_count = request.form['text_reviews_count']
    publication_date = request.form['publication_date']
    publisher = request.form['publisher']
    no_of_copies_total = request.form['no_of_copies_total']
    no_of_copies_current = request.form['no_of_copies_current']

    #Check if BookID already exists
    existing_book = Books.query.filter_by(bookID=bookID).first()
    if existing_book:
        flash("Book ID already exists. Please use a unique Book ID.", 'error')
        return redirect(url_for('index'))


    #Check number of copies is not negative
    try:
        no_of_copies_total = int(no_of_copies_total)
        no_of_copies_current = int(no_of_copies_current)
        if no_of_copies_total < 0 or no_of_copies_current < 0:
            raise ValueError("Number of copies cannot be negative.")
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))
    
    #Check number of pages is not negative
    try:
        num_pages = int(num_pages)
        if num_pages < 0:
            raise ValueError("Number of pages cannot be negative.")
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))

    #Check avergae rating is between 0 and 5
    try:
        average_rating = int(average_rating)
        if average_rating < 0 or average_rating > 5:
            raise ValueError("Avergae rating should be between 0 and 5.")
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('index'))


    new_book = Books(
        bookID=bookID,
        title=title,
        authors=authors,
        average_rating=average_rating,
        isbn=isbn,
        isbn13=isbn13,
        language_code=language_code,
        num_pages=num_pages,
        ratings_count=ratings_count,
        text_reviews_count=text_reviews_count,
        publication_date=publication_date,
        publisher=publisher,
        no_of_copies_total=no_of_copies_total,
        no_of_copies_current=no_of_copies_current
    )
    db.session.add(new_book)
    db.session.commit()
    flash("Book added successfully!", 'success')
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_book():
    bookID = request.form['bookID']
    book_to_delete = Books.query.filter_by(bookID=bookID).first()

    if book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()
        flash(f"Book with ID {bookID} has been deleted successfully.", 'success')
    else:
        flash(f"Book with ID {bookID} does not exist.", 'error')

    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    search_results = Books.query.filter(
        (Books.title.ilike(f'%{query}%')) |
        (Books.authors.ilike(f'%{query}%')) |
        (Books.isbn.ilike(f'%{query}%')) |
        (Books.isbn13.ilike(f'%{query}%'))
    ).all()
    return render_template('index.html', books=search_results, query=query)

if __name__ == '__main__':
    with app.app_context():
        print("Creating the database tables...")
        db.create_all()
        print("Database tables created.")
    app.run(debug=True)
