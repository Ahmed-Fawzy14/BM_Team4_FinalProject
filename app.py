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
    num_pages = db.Column(db.Integer)
    ratings_count = db.Column(db.Integer)
    text_reviews_count = db.Column(db.Integer)
    publication_date = db.Column(db.String(250))
    publisher = db.Column(db.String(250))
    no_of_copies_total = db.Column(db.Integer)
    no_of_copies_current = db.Column(db.Integer)

    def loan_book(self):
        if self.no_of_copies_current > 0:
            self.no_of_copies_current -= 1
            return True
        return False

    def return_book(self):
        if self.no_of_copies_total - self.no_of_copies_current > 0:
            self.no_of_copies_current += 1
            return True
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books_list')
def books_list():
    books = Books.query.all()
    return render_template('books_list.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
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
        no_of_copies_current = no_of_copies_total

        existing_book = Books.query.filter_by(bookID=bookID).first()
        if existing_book:
            flash("Book ID already exists. Please use a unique Book ID.", 'error')
            return redirect(url_for('add_book'))

        try:
            no_of_copies_total = int(no_of_copies_total)
            no_of_copies_current = int(no_of_copies_current)
            if no_of_copies_total < 0 or no_of_copies_current < 0:
                raise ValueError("Number of copies cannot be negative.")
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('add_book'))
        
        try:
            num_pages = int(num_pages)
            if num_pages < 0:
                raise ValueError("Number of pages cannot be negative.")
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('add_book'))

        try:
            average_rating = float(average_rating)
            if average_rating < 0 or average_rating > 5:
                raise ValueError("Average rating should be between 0 and 5.")
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('add_book'))

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
        return redirect(url_for('books_list'))
    
    return render_template('add_book.html')

@app.route('/delete_book', methods=['GET', 'POST'])
def delete_book():
    if request.method == 'POST':
        bookID = request.form['bookID']
        book_to_delete = Books.query.filter_by(bookID=bookID).first()

        if book_to_delete:
            db.session.delete(book_to_delete)
            db.session.commit()
            flash(f"Book with ID {bookID} has been deleted successfully.", 'success')
        else:
            flash(f"Book with ID {bookID} does not exist.", 'error')

        return redirect(url_for('books_list'))
    
    return render_template('delete_book.html')

@app.route('/loan_book', methods=['GET', 'POST'])
def loan_book():
    if request.method == 'POST':
        bookID = request.form['bookID']
        book = Books.query.filter_by(bookID=bookID).first()

        if book and book.loan_book():
            db.session.commit()
            flash(f"Book {book.title} loaned out successfully.", 'success')
        else:
            flash("Loan failed. Book may not be available.", 'error')

        return redirect(url_for('books_list'))
    
    return render_template('loan_book.html')

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        bookID = request.form['bookID']
        book = Books.query.filter_by(bookID=bookID).first()

        if book and book.return_book():
            db.session.commit()
            flash(f"Book {book.title} returned successfully.", 'success')
        else:
            flash("Return failed. No copies are currently loaned out.", 'error')

        return redirect(url_for('books_list'))
    
    return render_template('return_book.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    search_results = Books.query.filter(
        (Books.title.ilike(f'%{query}%')) |
        (Books.bookID == query) |
        (Books.authors.ilike(f'%{query}%')) |
        (Books.isbn == query) 
    ).all()
    if not search_results:
        flash(f"No books found for search query: {query}", 'error')
    return render_template('books_list.html', books=search_results, query=query)

if __name__ == '_main_':
    with app.app_context():
        print("Creating the database tables...")
        db.create_all()
        print("Database tables created.")
    app.run(debug=True)