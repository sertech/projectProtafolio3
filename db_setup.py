from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
        __tablename__ = 'user'
        t_id = Column(Integer, primary_key=True)
        t_name = Column(String(250), nullable=False)
        t_email = Column(String(250), nullable=False)
        t_picture = Column(String(250))

class Category(Base):
    __tablename__ = 'category'
    # table fields
    t_id = Column(Integer, primary_key=True)
    t_catName = Column(String(250), nullable=False)

    # table relations
    t_userId = Column(Integer, ForeignKey('user.t_id'))
    t_relationU = relationship(User)


    @property
    def serialize(self):
        """ Return object data in a easily serializeable format"""
        return {
            'name': self.t_catName
        }

class Item(Base):
    __tablename__ = 'item'

    # table fields
    t_id = Column(Integer, primary_key=True)
    t_itemName = Column(String(100), nullable=False)
    t_itemDescription = Column(String(250), nullable=False)

    # table relations
    t_userId = Column(Integer, ForeignKey('user.t_id'))
    t_relationU = relationship(User)

    t_catId = Column(Integer, ForeignKey('category.t_id'))
    t_relationC = relationship(Category)    
    
    @property
    def serialze(self):
        """ Return object data in a easily serializeable format """
        return {
            'name': self.t_itemName,
            'description': self.t_itemDescription
        }

engine = create_engine('sqlite:///catalogApp.db')

Base.metadata.create_all(engine)