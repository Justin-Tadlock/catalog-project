import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }

class Sub_Category(Base):
    __tablename__ = "sub_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    cat_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'cat_id': self.cat_id,
            'user_id': self.user_id
        }

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    sub_category = Column(String(50), nullable=False)
    picture = Column(String(1000), nullable=True)
    link = Column(String(1000), nullable=True)
    description = Column(String(255), nullable=False)

    cat_id = Column(Integer, ForeignKey('category.id'))
    sub_cat_id = Column(Integer, ForeignKey('sub_category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'sub_category': self.sub_category,
            'picture': self.picture,
            'link': self.link,
            'description': self.description,
            'cat_id': self.cat_id,
            'sub_cat_id': self.sub_cat_id,
            'user_id': self.user_id
        }

### Insert at end of file ###
engine = create_engine('sqlite:///item_catalog.db')

Base.metadata.create_all(engine)
