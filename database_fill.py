from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Book, Base, Category, User, Package, Packagebook
from functions import getBookDetails, generateComments
import random
import string

print("Setting up the database for BookBuddy...")
engine = create_engine('sqlite:///bookmarket.db')
print("*** Done setting up the database for BookBuddy! ***")

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Create two dummy users
print ("Filling the database with sample data...")
firstUser = User(
    name="Jacob Svensson", email="jsvensson@firma.se",
    picture="/static/user.png")
secondUser = User(
    name="John Smith", email="johnsmith@gmail.com",
    picture="/static/user.png")

# Add both users and make the first user (firstUser) the current user
userExists1 = session.query(User).filter_by(email=firstUser.email).first()
if userExists1 is None:
    session.add(firstUser)
    session.commit()
else:
    firstUser = userExists1

userExists2 = session.query(User).filter_by(email=secondUser.email).first()
if userExists2 is None:
    session.add(secondUser)
    session.commit()
else:
    secondUser = userExists2

currentUser = session.query(User).filter_by(id=firstUser.id).one()

# -------------------------------------------------------- #
#                Add books using isbns                     #
# -------------------------------------------------------- #

# The list of ISBNS to add to the database, the details of the book are
# dynamically collected from google Books API using the function getBookDetails
isbns = ['9780552149518','9780747532743','9780747538486','9780552150736',
         '9780747551003','9780747581086','9780747591054','9780747546290',
         '9781904233657','9780747550990','9780552151764','9781904233886',
         '9780330457729','9780552151696','9780099450252','9781904233916',
         '9781847245458','9780747566533','9780099464464','9780141017891',
         '9780099429791','9780593054277','9780552997041','9781905654284',
         '9780747546245','9780747591061','9781849163422','9780752837505',
         '9780349116754','9780718147655','9780006512134','9780099387916',
         '9780752877327','9780755309511','9781841953922','9780091889487',
         '9780747599876','9780749397548','9780563384304','9780330507417',
         '9781861976123','9780590660549','9780755331420','9781849162746',
         '9780330367356','9780141020525','9780722532935','9780552996006',
         '9780099487821','9780141011905','9780718154776','9780099457169',
         '9780330332774','9780241003008','9780747582977','9781846051616',
         '9780718147709','9780755307500','9780141030142','9780007110926',
         '9780330448444','9780747561071','9780701181840','9780099771517',
         '9780563384311','9780590112895','9780718148621','9781904994367',
         '9781861978769','9780718152437','9780140276336','9780007156108',
         '9780593059258','9780752893686','9780007207329','9780552998482',
         '9780718144395','9780006498407','9780747563204','9781847670946',
         '9780007232741','9780099419785','9780747581109','9780099406136',
         '9780552149525','9780140237504','9780593050545','9780718144845',
         '9780552771153','9780141019376','9780552772747','9780552773898',
         '9780141022925','9780316731317','9781904994497','9780439993586',
         '9780552771108','9780552997034','9780099506928','9781846053443']


for isbn in isbns:

    currentbook = getBookDetails(isbn)

    # if getBookDetails returns a proper response
    if 'error' not in currentbook and 'nobook' not in currentbook:

        # Check if the category exists already, otherwise add a category
        # -------------------------------------------------------------

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

        # Check if the book (to be added) exists by finding all books with the
        # same isbn and the same user_id. Two different users can have in their
        # stores the same book.
        # ---------------------------------------------------------------------

        oldBook = session.query(Book).\
            filter_by(isbn=isbn, user_id=currentUser.id).first()

        if oldBook is not None:
            pass
            # print ('The book with isbn: %s already exists' % isbn)
        else:

            # The condition of the book is randomly generated between 1 and 5.
            # The price of the book is randomly selected between 4 and 20. The
            # comments are generate randomly as a sentence  of 4 words by the
            # function generateComments. The user of all books is currentUser,
            # who is for now firstUser.

            thisBook = Book(isbn=isbn, title=currentbook["title"],
                            description=currentbook["description"],
                            language=currentbook["language"],
                            pageCount=currentbook["pageCount"],
                            image=currentbook["image"],
                            author=currentbook["author"],
                            condition=random.randint(1, 5),
                            price=random.randint(4, 20),
                            comments=generateComments(),
                            user=currentUser,
                            category=currentCategory)
            session.add(thisBook)
            session.commit()

            # print ("added book:  %s!" % currentbook["title"])

# Now we will associate half of the books to firstUser and half to secondUser
# We find the total number of books added and find its half

booksCount = session.query(Book).count()
if booksCount % 2:
    halfBooks = booksCount/2
else:
    halfBooks = (booksCount+1)/2

firstUserBooks = session.query(Book).limit(halfBooks)
for book in firstUserBooks:
    book.user_id = firstUser.id
    session.add(book)
    session.commit()

firstUserBooksList = [] 
for book in firstUserBooks:
    firstUserBooksList.append(book.id)

secondUserBooks = session.query(Book).offset(halfBooks)
for book in secondUserBooks:
    book.user_id = secondUser.id
    session.add(book)
    session.commit()

secondUserBooksList = []
for book in secondUserBooks:
    secondUserBooksList.append(book.id)

# -------------------------------------------------------- #
#      Add 10 packages using isbns for each user           #
# -------------------------------------------------------- #

for thisUser in range(1, 3):

    for x in range(1, 11):

        # (1) Generate a random list of books between 2 and 14 books
        # Depending on the user, the list is generated
        if thisUser == 1:
            packageBooks = random.sample(firstUserBooksList,
                                         random.randint(2, 14))
        else:
            packageBooks = random.sample(secondUserBooksList,
                                         random.randint(2, 14))

        # (2) Price of the package is between 10 and 25 dollars
        packagePrice = random.randint(10, 25)

        # (3) Create a new package for the specified user
        newPackage = Package(user_id=thisUser, price=packagePrice)
        session.add(newPackage)
        session.commit()

        # (4) Add the books to the books' package
        for book in packageBooks:
            bookToAdd = session.query(Book).filter_by(id=book).one()
            newAssociation = Packagebook(package=newPackage, book=bookToAdd)
            session.add(newAssociation)
            session.commit()

print("*** Done filling up the database with sample data! ***")
