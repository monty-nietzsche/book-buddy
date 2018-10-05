from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
import time
import random
import string
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from flask import session as login_session

from functions import getBookDetails, getLanguagesList

from database_setup import Book, Base, Category, User, Package, Packagebook

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

engine = create_engine('sqlite:///bookmarket.db',
                       connect_args={'check_same_thread': False})
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


app = Flask(__name__)
app_path =""


CLIENT_ID = json.loads(
    open(app_path + 'client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Oldbooks Market"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """Dislays the login screen."""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state,
                           categories=getCategories(),
                           languages=getLanguages(),
                           client_id=CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connect to google sign-in service."""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(app_path + 'client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['type'] = 'real'

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1><br>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;">'
    flash("You are now logged in as %s" % login_session['username'])
    print("done!")

    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """Disconnects from Google sign-in service."""
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('User is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have been successfully logged out!")
        # return response
        return redirect(url_for('showBooks'))
    else:
        response = make_response(json.dumps('''Failed to revoke token for
        given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        flash("Failed to revoke token! Please try again later!")
        # return response
        return redirect(url_for('showBooks'))


@app.route('/dummyconnect', methods=['POST'])
def connectDummy():
    """
    Connect a dummy user to the system.

    The function receives the variable 'dummy' which contains the
    id of the dummy user. Using this id, we query the database,
    receive the details of the dummy user and fill in them in the
    login_session.
    """
    dummy_id = int(request.args.get('dummy'))
    print(dummy_id)
    users = session.query(User).all()
    for user in users:
        print(user.name, user.id)
    thisUser = session.query(User).filter_by(id=dummy_id).first()

    if thisUser is not None:

        login_session['username'] = thisUser.name
        login_session['picture'] = thisUser.picture
        login_session['email'] = thisUser.email
        login_session['user_id'] = thisUser.id
        login_session['type'] = 'dummy'

        # Use the data collected about the dummy user, create
        # a welcome message and send it back to the python function

        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']
        output += '!</h1><br>'
        output += '<img src="'
        output += login_session['picture']
        output += ''' " style = "width: 300px; height: 300px;
            border-radius: 150px;">'''

        # Send a flash message about the dummy user logged in

        flash("You are now logged in as dummy user %s."
              % login_session['username'])
        return output
    else:
        # Dummy user could not log in, send an error message
        errorMessage = "This dummy user cannot log in. Please try again later"
        flash(errorMessage)
        return errorMessage


@app.route('/dummydisconnect')
def disconnectDummy():
    """
    Disconnect the dummy user from the system.

    It is done through deleting the variables in the login session. It checks
    first if there is a dummy user logged in, it there is, delete the variables
    in the login session. If no (dummy) user logged in, return a flash message!
    """
    if 'username' in login_session and login_session['type'] == 'dummy':
        dummyUser = login_session['username']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['type']

        flash("Dummy user %s has been successfully disconnected!" % dummyUser)
        return redirect(url_for('showBooks'))
    else:
        flash("No dummy user is connected!")
        return redirect(url_for('showBooks'))

# User Helper Functions


def createUser(login_session):
    """Create a new user."""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Get the user_id and return the corresponding user object."""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Find the user_id corresponding a given email."""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


###########################################################################
# Main Application routes
###########################################################################
@app.route('/')
@app.route('/books')
def showBooks():
    """Show three main pieces of information from the database (Homepage).

    (1) Latest packages: It queries the database to find the latest five
        packages created. For each of these five packages, it collectes
        a 4-tuple (package_id, number of books in the package, the price of the
        package, the image of the first book in the package).
    (2) Latest books: It queries the database to find the latest five books
        created. For each of these five books, it collects a pair (book
        object, category name). The book object contains only 'category_id'
        so the category name is fetched from the category table.
    (3) Cheapest books: It queries database to find the cheapest five books.
        For each of these five books, it collects a pair (book object, category
        name).
    These three pieces of information are then sent to template 'books.html'.
    """
    # ----------------- #
    #  LATEST PACKAGES  #
    # ----------------- #

    # Find the number of books per package as well as the first featured book.
    # Send the id and the image of the featured book to template

    packages = session.query(Packagebook.package_id,
                             func.count(Packagebook.book_id).label('antal'))\
        .group_by(Packagebook.package_id).all()
    packageDetails = []

    for package in packages:
        packageItem = []

        # Find the first book_id of each package
        firstBook = session.query(Packagebook)\
            .filter_by(package_id=package.package_id).first()

        # Find the package oject for each package_id
        thisPackage = session.query(Package)\
            .filter_by(id=package.package_id).first()

        # Find the book object for the first book in the package
        mainBook = session.query(Book).filter_by(id=firstBook.book_id).one()

        # Collect the package details: package_id, number of books in
        # the package (antal), the package price, the first book's image.
        packageItem.append(package.package_id)
        packageItem.append(package.antal)
        packageItem.append(thisPackage.price)
        packageItem.append(mainBook.image)

        packageDetails.append(packageItem)

        # Reverse to get the list in descending chronological order
        packageDetails = list(reversed(packageDetails))

        # Take the first five packages
        packageDetails = packageDetails[:5]

    # ---------------- #
    #   LATEST BOOKS   #
    # ---------------- #

    # Find the the latest five books created and for each book
    # create Book-Category pair and send them to the template
    items = session.query(Book, Category).join(Category)\
        .filter(Book.category_id == Category.id)\
        .order_by(Book.created.desc()).limit(5)
    currentItems = []
    for y in items:
        x = y.Book
        item = {}
        for attr, value in x.__dict__.items():
            item[attr] = value
        item['c_name'] = y.Category.name
        currentItems.append(item)

    # ---------------- #
    #  CHEAPEST BOOKS  #
    # ---------------- #

    # Find the cheapest books and send them to the template
    # Create Book-Category tuple and send them to the template
    items = session.query(Book, Category).join(Category)\
        .filter(Book.category_id == Category.id).order_by(Book.price).limit(5)
    cheapItems = []
    for y in items:
        x = y.Book
        item = {}
        for attr, value in x.__dict__.items():
            item[attr] = value
        item['c_name'] = y.Category.name
        cheapItems.append(item)

    return render_template('books.html', books=currentItems,
                           packages=packageDetails, cheapbooks=cheapItems,
                           categories=getCategories(),
                           languages=getLanguages())


@app.route('/book/new', methods=['GET', 'POST'])
def newBook():
    """Create a new book.

    (*) The function checks whether an unauthorized user is trying to
        create a new book object. Only logged-in users are allowed to
        create a new book. If no user is logged in then the visitor is
        directed to the login page.
    (*) If the method is POST, the function collects the form data. (isbn,
        condition, price, comments). It sends the isbn to the function
        getBookDetails in order to retrieve information about the book from
        Google Books API. It getBookDetails returns 'error' or 'nobook', an
        appropriate error (flash) message is sent and the homepage is shown.
        If getBookDetails returns a proper response (book details), this
        response, combined with condition, price and comments are used to
        create new book object.
    (*) If the method is GET, the template 'newbook.html' is rendered and
        sent to browser.
    """
    # This page can only be accessed by a logged-in user.
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':

        # Find the current user
        user_id = login_session['user_id']
        currentUser = session.query(User).filter_by(id=user_id).one()

        # Collect the information from the form
        isbn = request.form['isbn']
        condition = request.form['condition']
        price = request.form['price']
        comments = request.form['comments']

        currentbook = getBookDetails(isbn)

        # if getBookDetails returns an error (error from Google Books)
        if 'error' in currentbook:

            flash("Error retrieving details for the book with ISBN: %s.\
                Please try again later!" % isbn)
            return redirect(url_for('showBooks'))

        # No book in Google Books database with that ISBN exists
        elif 'nobook' in currentbook:

            flash("No book with ISBN: %s exists!\
                Please check your ISBN and try again!" % isbn)
            return redirect(url_for('showBooks'))

        # The book exists and getBookDetails() returns data
        else:

            # Check if the category exists already, otherwise add a category
            # --------------------------------------------------------------
            categoryName = currentbook["category"]
            oldCategory = session.query(Category).\
                filter_by(name=categoryName).first()

            if oldCategory is not None:
                currentCategory = oldCategory
                # print 'Category already exists'
            else:
                currentCategory = Category(name=categoryName)
                session.add(currentCategory)
                session.commit()

            # Check if the book (to be added) exists by finding all books with
            # the same isbn and the same user_id. Two different users can have
            # in their stores the same book.
            # -----------------------------------------------------------------

            oldBook = session.query(Book).\
                filter_by(isbn=isbn, user_id=currentUser.id).first()

            if oldBook is not None:
                flash("The book '%s' already exists!" % oldBook.title)
                return redirect(url_for('showBook', book_id=oldBook.id))
            else:
                thisBook = Book(isbn=isbn, title=currentbook["title"],
                                description=currentbook["description"],
                                language=currentbook["language"],
                                pageCount=currentbook["pageCount"],
                                image=currentbook["image"],
                                author=currentbook["author"],
                                condition=condition, price=price,
                                comments=comments, user=currentUser,
                                category=currentCategory)

                session.add(thisBook)
                session.commit()
                flash("The book '%s' has been successfully added!"
                      % currentbook["title"])
                return redirect(url_for('showBook', book_id=thisBook.id))

    else:

        return render_template('newBook.html',
                               categories=getCategories(),
                               languages=getLanguages())


@app.route('/book/<int:book_id>/show')
def showBook(book_id):
    """Show detailed information about a given book.

    args: book_id (integer)
    (*) If there is no book whose id is book_id, an error (flash) message
        is sent and the home page is shown.
    (*) If the book exists, the function retrieves all information about
        the book:
        - book object
        - category name
        - packages (package_id, number of books, package price and image
          of first book).
        These data pieces are sent to the template 'showBook.html'.
    """
    # Try to retrieve the book whose id equals book_id
    currentBook = session.query(Book).filter_by(id=book_id).first()

    if currentBook is not None:

        # Find the category of the book so to show the name of the category
        currentCategory = session.query(Category).\
            filter_by(id=currentBook.category_id).one()

        # Find out if the book belongs to package and if yes, which ones
        potentialPackages = session.query(Packagebook).\
            filter_by(book_id=book_id).all()
        packageDetails = []

        # Find the packages to which the book eventually belongs
        if potentialPackages is not None:
            inPackages = []

            # Add to inPackages all package_id of the packages to which the
            # book belongs.
            for x in potentialPackages:
                inPackages.append(x.package_id)

            # Out of all packages, select those in our list of packages
            packages = session.query(Packagebook.package_id,
                                     func.count(Packagebook.book_id).
                                     label('antal')).\
                group_by(Packagebook.package_id).all()

            for package in packages:

                # Out of the packagesm select those in the list inPackages[]
                # and collect all information about it i.e. package_id, number
                # of books in the package (antal), the package price, the first
                # book image.

                if inPackages.count(package.package_id) == 1:

                    packageItem = []
                    firstBook = session.query(Packagebook).\
                        filter_by(package_id=package.package_id).first()
                    thisPackage = session.query(Package).\
                        filter_by(id=package.package_id).first()
                    mainBook = session.query(Book).\
                        filter_by(id=firstBook.book_id).one()
                    packageItem.append(package.package_id)
                    packageItem.append(package.antal)
                    packageItem.append(thisPackage.price)
                    packageItem.append(mainBook.image)
                    packageDetails.append(packageItem)

        # Find the creator of the book as well as the user logged-in and
        # create variables: loggedIn that takes True when a user is logged in,
        # and False otherwise and can_edit taking True when the logged-in user
        # can edit(delete) the book, False otherwise.
        # If the loggedUser is the same creator of the book, then they are
        # allowed to edit. Then send the variables loggedIn and can_edit to
        # the template.

        can_edit = False
        creator = getUserInfo(currentBook.user_id)

        if 'user_id' in login_session:
            loggedUser = getUserInfo(login_session['user_id'])
            loggedIn = True
            can_edit = (loggedUser.id == creator.id)
        else:
            loggedIn = False
            loggedUser = None

        return render_template('book.html', book=currentBook,
                               category=currentCategory,
                               packages=packageDetails,
                               categories=getCategories(),
                               languages=getLanguages(),
                               loggedIn=loggedIn,
                               can_edit=can_edit)

    else:

        # The book with the book_id does not exist.
        flash('''The book you are trying to acccess does not exist anymore.
              Please choose another book!''')
        return redirect(url_for('showBooks'))


@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
def editBook(book_id):
    """Edit the book with the given id: book_id.

    This function allows the editing of the book with id equal to book_id.
    It takes as argument book_id and returns a updated book object.
    If no book exists with an id equal to book_id, then an error (flash)
    message is returned and the page of the book is shown. If the logged
    in user is not authorized to edit the book (not the owner), an
    appropriate error (flash) message is sent and the page of the book is
    shown.
    """
    # This page can only be accessed by a logged-in user.
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':

        # Find the book object with the corresponding book_id
        thisBook = session.query(Book).filter_by(id=book_id).one()

        # Collect information from the form and update the book
        # object with this information

        if request.form['condition'] is not None:
            thisBook.condition = request.form['condition']

        if request.form['price'] is not None:
            thisBook.price = request.form['price']

        thisBook.comments = request.form['comments']

        session.add(thisBook)
        session.commit()

        flash("'%s' has been successfully edited!" % thisBook.title)

        return redirect(url_for('showBook', book_id=book_id))

    else:

        # Find the book object with corresponding book_id and the
        # current user. If the book object does not exist, then there
        # is no book to edit and an error message is returned. If the
        # book object exists but the current (logged in) user is the
        # not the owner, then an error message (no authorization) is
        # returned. Otherwise, the page editbook.html is rendered and
        # sent to browser.

        item = session.query(Book).filter_by(id=book_id).first()
        currentUser = login_session["user_id"]

        if item is not None:

            # If the user requesting editing is not the owner,
            # editing is denied! If it is the owner, render the
            # template of editbook.html

            if currentUser != item.user_id:

                flash("You are not authorized to edit this book!")
                return redirect(url_for('showBook', book_id=item.id))

            else:

                return render_template('editbook.html',
                                       book_id=book_id,
                                       book=item,
                                       categories=getCategories(),
                                       languages=getLanguages())
        else:

            flash('''The book you are trying to edit does not exist anymore!
                  Please choose another book!''')
            return redirect(url_for('showBooks'))


@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
def deleteBook(book_id):
    """Delete the book with the given id: book_id.

    This function allows the deletion of the book with id equal to book_id.
    It takes as argument book_id and returns a deleted book object.
    If no book exists with an id equal to book_id, then an error (flash)
    message is returned and the homepage is shown. If the logged-in user
    is not authorized to delete the book (not the owner), an appropriate error
    (flash) message is sent and the page of the book is shown.
    """
    # This page can only be accessed by a logged-in user.
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':

        # Delete the book
        thisBook = session.query(Book).filter_by(id=book_id).one()
        session.delete(thisBook)
        session.commit()

        # Delete all book-package associations
        bookPackages = []
        thisBookAssociations = session.query(Packagebook).\
            filter_by(book_id=book_id)
        if thisBookAssociations is not None:
            for association in thisBookAssociations:
                bookPackages.append(association.package_id)
                session.delete(association)
                session.commit()
        flash("The book '%s' has been deleted!" % thisBook.title[:60])

        # After the book has been deleted, check if there are empty packages or
        # ones with just one book in them. If there are, find them and delete
        # them.

        for package in bookPackages:

            # For each package, find the number of books it holds and store it
            # in the packageBooks variable.
            packageBooks = session.query(Packagebook).\
                           filter_by(package_id=package).count()

            # if the package has no books or one book in it, delete it.
            # Of course, all associations it has with other books shall also
            # be deleted.

            if packageBooks < 2:
                thisPackage = session.query(Package).\
                    filter_by(id=package).one()
                session.delete(thisPackage)
                session.commit()
                thisPackageAssociations = session.query(Packagebook).\
                    filter_by(package_id=package)
                for association in thisPackageAssociations:
                    session.delete(association)
                    session.commit()

                flash('''Package #0000%s had %s book(s) left in it and has
                therefore been deleted!''' % (package, packageBooks))

        return redirect(url_for('showBooks'))

    else:

        # Find the book object with corresponding book_id and the
        # current user. If the book object does not exist, then there
        # is no book to delete and an error message is returned. If the
        # book object exists but the current (logged in) user is the
        # not the owner, then an error message (no authorization) is
        # returned. Otherwise, the page deletebook.html is rendered and
        # sent to browser.

        item = session.query(Book).filter_by(id=book_id).first()
        currentUser = login_session["user_id"]

        if item is not None:

            # If the user requesting deletion is not the owner,
            # deletion is denied. Otherwise, the template 'deletebook.html'
            # is rendered and sent to browser.

            if currentUser != item.user_id:

                flash("You are not authorized to delete this book!")
                return redirect(url_for('showBook', book_id=item.id))

            else:

                return render_template('deletebook.html',
                                       book=item,
                                       categories=getCategories())

        else:

            flash('''The book you are trying to delete does not exist or has
                    been deleted. Please choose another book!''')
            return redirect(url_for('showBooks'))


@app.route('/package/<int:package_id>/books')
def showPackageBooks(package_id):
    """Display the book in the package with the given id: package_id.

    (1) If the package exists (there is a package object having package_id as
    an id , then the information about the books are collected and
    sent to the template.
    (2) If the package does not exist, then an error (flash) message is sent
    and the page that displays all packages is sent to browser.
    """
    # This package eventually holds the package object having id=package_id
    thisPackage = session.query(Package).filter_by(id=package_id).first()

    # If there is a package object with package_id. Find the sum of the prices
    # of all books in the package and substract it from the package price to
    # find the saving the user have made. Otherwise, send an error (flash)
    # message stating that the package does not exist anymore and show the
    # page showing all packages.

    if thisPackage is not None:

        normalCost = session.query(Packagebook.package_id,
                                   func.sum(Book.price).label('total')).\
                                   filter_by(package_id=package_id).\
                                   filter(Packagebook.book_id == Book.id).\
                                   group_by(Packagebook.package_id).one()

        saving = normalCost.total-thisPackage.price

        selectedBooks = session.query(Book).join(Packagebook).\
            filter(Book.id == Packagebook.book_id).\
            filter_by(package_id=package_id)

        # Find the creator of the book as well as the user logged-in and
        # create variables: loggedIn that takes True when a user is logged in,
        # and False otherwise and can_edit taking True when the logged-in user
        # can edit(delete) the book, False otherwise.

        can_edit = False
        creator = getUserInfo(thisPackage.user_id)

        if 'user_id' in login_session:
            loggedUser = getUserInfo(login_session['user_id'])
            loggedIn = True
            can_edit = (loggedUser.id == creator.id)
        else:
            loggedIn = False
            loggedUser = None

        return render_template('packagebooks.html',
                               package=thisPackage,
                               books=selectedBooks,
                               saving=saving, categories=getCategories(),
                               languages=getLanguages(),
                               loggedIn=loggedIn, can_edit=can_edit)

    else:

        flash('''The package you are trying to access does not exist anymore.
            Please choose another one below!''')
        return redirect(url_for('showPackages'))


@app.route('/package/new/', methods=['GET', 'POST'])
def newPackage():
    """Add a new package."""
    # Only logged-in are authorized to add a new package
    if 'username' not in login_session:
        return redirect('/login')

    currentUser = login_session['user_id']

    if request.method == 'POST':

        # Collect information from the form
        packageBooks = request.form.getlist('book[]')
        packagePrice = request.form['price']

        # Create a new empty package
        newPackage = Package(user_id=currentUser, price=packagePrice)
        session.add(newPackage)
        session.commit()

        # Add the books to the books' package
        for book in packageBooks:
            bookToAdd = session.query(Book).filter_by(id=book).one()
            newAssociation = Packagebook(package=newPackage, book=bookToAdd)
            session.add(newAssociation)
            session.commit()

        # Return the page showing books per package
        flash("Your package has been successfully created!")
        return redirect(url_for('showPackageBooks', package_id=newPackage.id))

    else:
        items = session.query(Book).filter_by(user_id=currentUser).\
            order_by(Book.title)
        return render_template('newpackage.html',
                               books=items,
                               categories=getCategories(),
                               languages=getLanguages())


@app.route('/package/<int:package_id>/edit', methods=['GET', 'POST'])
def editPackage(package_id):
    """Edit the package with the given id: package_id.

    This page is only for logged-in users.
    (1) If the method is POST, collect the information from the form
    and update the package object with package_id as an Id.
    (2) If the method is GET:
        (a) If no package exists with an id equal to package_id, then
            return an error (flash) message saying that the package does
            not exist (anymore). The page showing all packages is sent
            to the browser.
        (b) If the user trying to edit the the package is not the owner of
            the package, then return an error (flash) message saying that
            the user is not authorized to edit the package. The page showing
            all packages is sent to the browser.
        (c) If the package exists and its owner requests editing it, then
            render the template 'editPackage.html', along with the required
            data (selectedBooks, userbooks)
    """
    # This page can only be accessed by a logged-in user.
    if 'username' not in login_session:
        return redirect('/login')

    # Find the current user
    currentUser = login_session["user_id"]

    if request.method == 'POST':

        # Collect information from the form
        packageBooks = request.form.getlist('book[]')
        packagePrice = request.form['price']

        # Find the package and compare its stored price to the new price
        # Update if the prices are different
        currentPackage = session.query(Package).\
            filter_by(id=package_id, user_id=currentUser).one()

        if currentPackage.price != packagePrice:
                print("new price is %s" % packagePrice)
                currentPackage.price = packagePrice
                session.add(currentPackage)
                session.commit()

        # For each book already stored in the db, if they are not currently
        # selected, delete it from the database. Once done, for each of the
        # books newly selected, if they are not stored, add them.

        storedBooks = session.query(Packagebook).\
            filter_by(package_id=currentPackage.id)

        for book in storedBooks:
            if book.book_id not in packageBooks:
                session.delete(book)
                session.commit()

        for book_id in packageBooks:
            soughtBook = session.query(Packagebook).\
                filter_by(package_id=currentPackage.id,
                          book_id=book_id).first()
            if soughtBook is None:
                newAssociation = Packagebook(package_id=currentPackage.id,
                                             book_id=book_id)
                session.add(newAssociation)
                session.commit()

        flash("Your package has been successfully edited!")
        return redirect(url_for('showPackageBooks',
                                package_id=currentPackage.id))

    else:

        currentPackage = session.query(Package).\
            filter_by(id=package_id).first()

        if currentPackage is not None:

            # If the user requesting editing the package is not its owner,
            # editing is denied! Otherwise, collect the data about the books
            # currently in the package (selectedBooks) as well as all books of
            # the current user (userBooks) and send them to the template
            # 'editPackage.html'

            if currentUser != currentPackage.user_id:

                flash("You are not authorized to edit this package!")
                return redirect(url_for('showPackageBooks',
                                        package_id=currentPackage.id))

            else:

                selectedBooks = session.query(Book).\
                    filter_by(user_id=currentUser).join(Packagebook).\
                    filter(Book.id == Packagebook.book_id).\
                    filter_by(package_id=package_id)

                userBooks = session.query(Book).\
                    filter_by(user_id=currentUser).\
                    order_by(Book.title)

                return render_template('editpackage.html',
                                       package=currentPackage,
                                       selectedBooks=selectedBooks,
                                       books=userBooks,
                                       categories=getCategories(),
                                       languages=getLanguages())
        else:

            flash('''The package you are trying to edit does not exist anymore!
                Please choose another package!''')
            return redirect(url_for('showPackages'))


@app.route('/package/<int:package_id>/delete', methods=['GET', 'POST'])
def deletePackage(package_id):
    """Delete the package with the given id: package_id.

    This page is only for logged-in users.
    (1) If the method is POST, delete the package object with package_id
        as an Id. Proceed to delete all its associations with books in
        the table 'Packagebook'.
    (2) If the method is GET:
        (a) If no package exists with an id equal to package_id, then
            return an error (flash) message saying that the package does
            not exist (anymore). The page showing all packages is sent
            to the browser.
        (b) If the user trying to delete the the package is not the owner of
            the package, then return an error (flash) message saying that
            the user is not authorized to edit the package. The page showing
            all packages is sent to the browser.
        (c) If the package exists and its owner requests deleting it, then
            render the template 'editPackage.html', along with the required
            data (selectedBooks).
    """
    # This page can only be accessed by a logged-in user.
    if 'username' not in login_session:
        return redirect('/login')

    # Find the current user
    currentUser = login_session["user_id"]

    if request.method == 'POST':

        # Find the package (thisPackage) having package_id as an id and
        # delete it. Find in the table 'Packagebook' any associations between
        # thisPackage and books and delete them too. Send a flash message once
        # the deletion has been completed and show the page of all package.

        thisPackage = session.query(Package).\
            filter_by(id=package_id, user_id=currentUser).one()
        session.delete(thisPackage)
        session.commit()

        thisPackageAssociations = session.query(Packagebook).\
            filter_by(package_id=package_id)

        if thisPackageAssociations is not None:
            for association in thisPackageAssociations:
                session.delete(association)
                session.commit()

        flash("Package #0000%s has been successfully deleted!" % package_id)
        return redirect(url_for('showPackages'))

    else:

        # Find the package (thisPackage) having package_id. If it doesn't exist
        # send an error (flash) message and show the page of all packages. If
        # the package exists, check if the user trying to delete it is actually
        # its owner. If it is not, show an error (flash) message and return the
        # page of all packages. If it is, render template 'deletepackage.html'
        # along with the data needed (selectedBooks).

        thisPackage = session.query(Package).\
            filter_by(id=package_id).first()

        if thisPackage is None:

            # No package has package_id as an id. Show an error message.
            flash('''The package you're trying to delete doesn't exist anymore.
            Please choose another package below!''')
            return redirect(url_for('showPackages'))

        else:

            # If the user trying to delete the package is not its owner,
            # deletion is denied and error (flash) message is shown. Otherwise,
            # find all books in the package and send them to the template
            # 'deletepackage.html'

            if currentUser != thisPackage.user_id:

                flash("You are not authorized to delete this package!")
                return redirect(url_for('showPackageBooks',
                                        package_id=thisPackage.id))

            else:

                selectedBooks = session.query(Book).\
                    filter_by(user_id=currentUser).\
                    join(Packagebook).\
                    filter(Book.id == Packagebook.book_id).\
                    filter_by(package_id=package_id)

                return render_template('deletepackage.html',
                                       package=thisPackage,
                                       books=selectedBooks,
                                       categories=getCategories(),
                                       languages=getLanguages())


@app.route('/packages/')
def showPackages():
    """Display all packages.

    In order to display packages, the following info are needed: - package_id
    - the number of books in the package - the price of the package - the image
    of the first book in the package. The function collects this infomation and
    send it to template 'packages.html'.
    """
    # Find all tuples {package_id, number_of_books (antal)}
    packages = session.query(Packagebook.package_id,
                             func.count(Packagebook.book_id).label('antal')).\
        group_by(Packagebook.package_id).all()

    packageDetails = []

    for package in packages:
        packageItem = []

        # Find the package object and object of its first book
        firstBook = session.query(Packagebook).\
            filter_by(package_id=package.package_id).first()
        thisPackage = session.query(Package).\
            filter_by(id=package.package_id).first()
        mainBook = session.query(Book).filter_by(id=firstBook.book_id).one()

        # For each package, collect its id, the number of its books, is price
        # and the image of its first book.
        packageItem.append(package.package_id)
        packageItem.append(package.antal)
        packageItem.append(thisPackage.price)
        packageItem.append(mainBook.image)
        packageDetails.append(packageItem)

        # Reverse the order of the list so you have the latest package
        # appearing first.
        packageDetails = list(reversed(packageDetails))

    # Find out whether a user is logged in so a button 'New Package' is
    # rendered in the packages.html page.

    if 'user_id' in login_session:
        loggedIn = True
    else:
        loggedIn = False

    return render_template('packages.html',
                           packages=packageDetails,
                           categories=getCategories(),
                           languages=getLanguages(),
                           loggedIn=loggedIn)


@app.route('/category/<int:category_id>/books')
def showBooksPerCategory(category_id):
    """Display books per category.

    It takes category_id as an argument.
    It collects all book objects having that category_id and gets the name
    of the category from the table 'Category' and then sends both to the
    template 'bookspercategory.html'.
    """
    # Collect all books with a category_id equal to category_id
    items = session.query(Book).filter_by(category_id=category_id).all()

    # Get the category object with an id equals to category_id
    currentCategory = session.query(Category).filter_by(id=category_id).first()

    if currentCategory is not None and items is not None:

        # Collect the name of the book category
        cName = currentCategory.name

        # Find out whether the user is logged in and info to the template.
        if 'user_id' in login_session:
            loggedIn = True
        else:
            loggedIn = False

        return render_template('bookspercategory.html',
                               categoryName=cName,
                               books=items,
                               categories=getCategories(),
                               languages=getLanguages(),
                               loggedIn=loggedIn)

    else:

        # Either the category does not exist or there are no books with that
        # category. return an error (flash) message and show the home page.
        flash('''There are no books in your chosen category. Please use the
            side menu to browse by category!''')
        return redirect(url_for('showBooks'))


@app.route('/language/<string:lang>/books')
def showBooksPerLanguage(lang):
    """Display the list of books per language where language=lang.

    lang is two-character word serving as a symbol for a given language e.g.
    'de' for german. The function collects all books objects having 'lang' as
    a language property. The full name of the language is obtained using the
    function getLanguageName() which takes an abbreviation and returns the
    name of the lanugage in english. The book objects along with the language
    name are sent to to the template 'booksperlanguage.html'.
    """
    # Find all books having lang as a language attribute
    items = session.query(Book).filter_by(language=lang).all()

    if items is not None and len(items) != 0:

        # Find out whether the user is logged in and info to the template.
        # It is used to know whether to show the button [Add Book] or not.

        if 'user_id' in login_session:
            loggedIn = True
        else:
            loggedIn = False

        # If the list of book objects with lang as a language is not empty,
        # send it along with the name of the language to the template.

        return render_template('booksperlanguage.html',
                               books=items,
                               language=getLanguageName(lang),
                               categories=getCategories(),
                               languages=getLanguages(),
                               loggedIn=loggedIn)

    else:

        # The list of book objects with lang as a language is empty. Send an
        # error (flash) message and show the homepage.

        flash('''There are no books in your chosen language. Please use the
            side menu to browse by language!''')
        return redirect(url_for('showBooks'))


##########################################################################
#                Functions showing the user space                        #
##########################################################################
@app.route('/mybooks')
def showMyBooks():
    """Display the books of the logged-in user.

    The main argument to the function is collected from login_session and
    it is the id of the logged-in user found in login_session["user_id"].
    Once the user_id is collected, tuples of the book-CategoryName for all
    books belonging to the logged-in user. This data is then sent to template
    'mybooks.html'.
    """
    # Only logged in users can show their books. If no user is logged in,
    # an error (flash) message is displayed and the homepage is sent to
    # browser.
    if 'user_id' not in login_session:

        flash("You have to be logged in to access user-specific content!")
        return redirect(url_for('showBooks'))

    else:

        # Create Book-CategoryName tuple and send them to the template
        items = session.query(Book, Category).join(Category).\
            filter(Book.category_id == Category.id,
                   Book.user_id == login_session["user_id"]).\
            order_by(Book.created.desc()).all()

        currentItems = []
        for y in items:
            x = y.Book
            item = {}
            for attr, value in x.__dict__.items():
                item[attr] = value
            item['c_name'] = y.Category.name
            currentItems.append(item)

    return render_template('mybooks.html',
                           books=currentItems,
                           categories=getCategories(),
                           languages=getLanguages(),
                           user=login_session["username"])


@app.route('/mypackages/')
def showMyPackages():
    """Display all packages of the logged-in user.

    The main argument to the function is collected from login_session
    and it is the id of the logged-in user found in login_session["user_id"].
    Once the user_id is collected, 4-tuple is created for each package of the
    logged-in user i.e. (package_id, number of books, price, image of the first
    book). This data is then sent to template 'mypackages.html'.
    """
    # Only logged in users can show their packages. If no user is logged in,
    # an error (flash) message is displayed and the homepage is sent to
    # browser.
    if 'user_id' not in login_session:

        flash("You have to be logged in to access user-specific content!")
        return redirect(url_for('showBooks'))

    else:

        # From the table 'Packagebook', create pais (package_id, number of
        # books (antal))
        packages = session.query(Packagebook.package_id,
                                 func.count(Packagebook.book_id).
                                 label('antal')).\
                                 group_by(Packagebook.package_id).all()

        packageDetails = []

        for package in packages:
            packageItem = []

            # For each package (package_id), find the corresponding package
            # object and the first book in it.

            firstBook = session.query(Packagebook).\
                filter_by(package_id=package.package_id).first()
            thisPackage = session.query(Package).\
                filter_by(id=package.package_id).first()
            mainBook = session.query(Book).\
                filter_by(id=firstBook.book_id).one()

            # Select only the packages of the specific user. For those,
            # collect package_id, number of books (antal), price and image
            # of the first book.

            if thisPackage.user_id == login_session["user_id"]:
                packageItem.append(package.package_id)
                packageItem.append(package.antal)
                packageItem.append(thisPackage.price)
                packageItem.append(mainBook.image)
                packageDetails.append(packageItem)

        packageDetails = list(reversed(packageDetails))

        return render_template('mypackages.html',
                               packages=packageDetails,
                               categories=getCategories(),
                               languages=getLanguages(),
                               user=login_session["username"])


##########################################################################
#                           API JSON FUNCTIONS                           #
##########################################################################
@app.route('/packages/json/')
def getPackagesInfo():
    """Create a JSON object returning data about all packages in the database.

    The output looks as follows:
    "Packages":[
    { "id":1,
      "price":19,
      "user":1
      "books":[
        {...},
            ...
        {...}
        ],
    }
    ...
    """
    packs = []

    # Retrieve all packages
    items = session.query(Package).all()

    for item in items:

        # For each package, serialize its properties
        packageDetails = item.serialize
        packageBooks = session.query(Packagebook).\
            filter_by(package_id=item.id).all()
        booksList = []

        # Create a property called 'Books' and within it, serialize all
        # invidual books
        for book in packageBooks:
            thisBook = session.query(Book).filter_by(id=book.book_id).one()
            booksList.append(thisBook.serialize)

        packageDetails["books"] = booksList
        packs.append(packageDetails)

    # Create and return a json object from the list created.
    return jsonify(Packages=packs)


@app.route('/books/json/')
def getBooksInfo():
    """Create a JSON object returning data about all books in the database.

    The output looks as follows (expand to see it):
    {
        "Books": [
        {
        "authors": "Khurshid Ahmad",
        "comments": "Lcqd ndtm irvx uwrfv frwzwkt.",
        "condition": 2,
        "description": "This volume maps the watershed areas between ...",
        "id": 1,
        "image": "http://books.google.com/books/content?id=TbaVkgEACAAJ",
        "isbn": "9789400717565",
        "language": "en",
        "pageCount": 150,
        "price": 13,
        "title": "Affective Computing and Sentiment Analysis",
        "user": 1
        },
        {
        "authors": "Alessandro Aldini,Roberto Gorrieri",
        "comments": "Jvkzaeso usdnmupzt zabmsewbv ydfq ljtmsr.",
        "condition": 3,
        "description": "The topics covered in this book include privacy ...",
        "id": 2,
        "image": "http://books.google.com/books/content?id=4V3sXpGrcFgC",
        "isbn": "9783642230813",
        "language": "en",
        "pageCount": 275,
        "price": 16,
        "title": "Foundations of Security Analysis and Design VI",
        "user": 1
        },
    }
    """
    # Retrieve all books, serialize their properties and create a json object
    # to be returned
    books = session.query(Book).all()
    return jsonify(Books=[i.serialize for i in books])


@app.route('/category/<int:category_id>/books/json/')
def getBooksPerCategoryInfo(category_id):
    """Create a JSON object returning data about all books per category.

    The output looks as
    follows:
    {
        "category":"Mathematics"
        "Books":[
        {...},
        {...},
        {...},
        {...},
        {...}
        ],
    }
    """
    # Retrieve all books in the given category specified by category_id
    books = session.query(Book).filter_by(category_id=category_id).all()

    # Find the name of the category
    currentCategory = session.query(Category).filter_by(id=category_id).first()

    # If the category_id does correspond to a valid category and there
    # are books in that category, create a dictionary Books with keys
    # 'category' and 'books' and return a json object out of it.
    # If the category does not correspond to a valid category, return an
    # error (flash) message and show the homepage.

    if currentCategory is not None and books is not None:
        Books = {}
        Books["category"] = currentCategory.name
        Books["Books"] = [i.serialize for i in books]
        return jsonify(Books)

    else:

        flash('''Your API query failed!
                There are no books in your chosen category!''')
        return redirect(url_for('showBooks'))


def getCategories():
    """Get all categories details in the database."""
    # Find all categories to populate the menu
    return session.query(Category).order_by(Category.name).\
        join(Book).\
        filter(Category.id == Book.category_id).all()


def getLanguages():
    """Get language names for all languages in the database."""
    # Find all language abbreviations as well as the number of books
    # for each language from the table 'Book'. The full name of each
    # language is found using the function getLanguageList() which
    # consists of correspondance dictionary between language
    # abbreviations and full bames. Combining these two pieces of
    # information, we obtain a list of tuples (language abbreviation,
    # language name, number of books for that language). A json object
    # is created out of this list and returned.

    languageList = getLanguagesList()
    booksLanguages = session.query(Book.language,
                                   func.count(Book.id).label('antal')).\
        group_by(Book.language)

    languagesDetails = []

    for language in booksLanguages:
        languageDetail = []
        languageDetail.append(language.language)
        languageDetail.append(languageList[language.language])
        languageDetail.append(language.antal)

        languagesDetails.append(languageDetail)

    return languagesDetails


def getLanguageName(lang):
    """Find the language name of the language whose abbreviation is lang."""
    # Import the language list dictionary and find the one corresponding
    # to the abbreviation lang
    return getLanguagesList()[lang]


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
