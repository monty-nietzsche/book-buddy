import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
        }


class Category (Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    isbn = Column(String(13), nullable=False)
    title = Column(String(250))
    author = Column(String(250))
    image = Column(String(500))
    description = Column(String(1000))
    language = Column(String(2))
    pageCount = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    price = Column(Integer, nullable=False)
    condition = Column(Integer)
    comments = Column(String(250))
    created = Column(DateTime, default=datetime.datetime.utcnow)
    category = relationship(Category)
    user = relationship(User)
    # We added this serialize function to be able to send JSON objects in a
    # serializable format

    @property
    def serialize(self):

        return {
            'isbn': self.isbn,
            'title': self.title,
            'authors': self.author,
            'image': self.image,
            'language': self.language,
            'pageCount': self.pageCount,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'condition': self.condition,
            'comments': self.comments,
            'user': self.user_id,
        }


class Package (Base):
    __tablename__ = 'package'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    price = Column(Integer, nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship(User)
    # We added this serialize function to be able to send JSON objects in a
    # serializable format

    @property
    def serialize(self):

        return {
            'id': self.id,
            'price': self.price,
            'user': self.user_id,
        }


class Packagebook (Base):
    __tablename__ = 'packagebook'

    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey('package.id'))
    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship(Book)
    package = relationship(Package)


engine = create_engine('sqlite:///bookmarket.db')
Base.metadata.create_all(engine)
