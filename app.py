from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key'



db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        new_user = User(username=username)
        new_user.set_password(password)  # This sets the password_hash attribute

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

    # Render the register template with appropriate headers to prevent caching
    response = make_response(render_template('register.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            session['is_admin'] = user.is_admin


            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
            return redirect(url_for('login'))

    # Render the login template with appropriate headers to prevent caching
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('login'))

@app.route('/books_list')
@login_required
def books_list():
    books = Books.query.all()
    return render_template('books_list.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

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
        #return redirect(url_for('books_list'))
    
    return render_template('add_book.html')


@app.route('/delete_book', methods=['GET', 'POST'])
@login_required
def delete_book():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        bookID = request.form['bookID']
        book_to_delete = Books.query.filter_by(bookID=bookID).first()

        if book_to_delete:
            db.session.delete(book_to_delete)
            db.session.commit()
            flash(f"Book with ID {bookID} has been deleted successfully.", 'success')
        else:
            flash(f"Book with ID {bookID} does not exist.", 'error')

        #return redirect(url_for('books_list'))
    
    return render_template('delete_book.html')


@app.route('/loan_book', methods=['GET', 'POST'])
@login_required
def loan_book():
    if request.method == 'POST':
        bookID = request.form['bookID']
        book = Books.query.filter_by(bookID=bookID).first()

        if book and book.loan_book():
            db.session.commit()
            flash(f"Book {book.title} loaned out successfully.", 'success')
        else:
            flash("Loan failed. Book may not be available.", 'error')

        #return redirect(url_for('books_list'))
    
    return render_template('loan_book.html')

@app.route('/return_book', methods=['GET', 'POST'])
@login_required
def return_book():
    if request.method == 'POST':
        bookID = request.form['bookID']
        book = Books.query.filter_by(bookID=bookID).first()

        if book and book.return_book():
            db.session.commit()
            flash(f"Book {book.title} returned successfully.", 'success')
        else:
            flash("Return failed. No copies are currently loaned out.", 'error')

        #return redirect(url_for('books_list'))
    
    return render_template('return_book.html')

def create_admin_user(admin_username, admin_password):
    
    print("Checking for admin user...")  # Debugging statement
    
    try:
        # Check if admin user already exists
        admin_user = User.query.filter_by(username=admin_username).first()
        print(f"Query executed. Result: {admin_user}")  # Debugging statement
        
        if admin_user is None:
            print("Admin user not found, creating one...")  # Debugging statement
            
            # Create a new user instance with the admin credentials
            admin_user = User(username=admin_username, is_admin=True)
            print(f"Created user instance: {admin_user}")  # Debugging statement
            
            admin_user.set_password(admin_password)
            print(f"Set password for admin user: {admin_user.password_hash}")  # Debugging statement
            
            # Add the admin user to the session and commit
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created and committed to the database.")  # Debugging statement
        else:
            print("Admin user already exists.")  # Debugging statement

    except Exception as e:
        print(f"An error occurred: {e}")  # Debugging statement



@app.route('/search', methods=['GET'])
@login_required
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user('admin', 'admin123')
    app.run(debug=True)
