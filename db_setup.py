#! /usr/bin/env python
# -*- coding: utf-8 -*-
import random
import string

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    BadSignature, SignatureExpired


Base = declarative_base()

# secret key generation

secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in range(32))


class User(Base):
    """This class represents the table for the user in the DB it stores the user's name, email, the
    link for the picture and the hash of the password not the password itself

    Arguments:
        Base {declarative_base} -- special class that correspond to tables in the DB
    """

    __tablename__ = 'user'
    t_id = Column(Integer, primary_key=True)
    t_name = Column(String(250), nullable=False)
    t_email = Column(String(250), nullable=False, unique = True)
    t_picture = Column(String(250))
    t_password_hash = Column(String(64))

    def hash_password(self, password):
        """This function hashes the password and store only the hash

        Arguments:
            password {string} -- A string containing the password sended by source
        """

        self.t_password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """This function checks a recieved password with a stored hash

        Arguments:
            password {string} -- A string containing the password sended by another source

        Returns:
            boolean -- if the hash matches the password recieved returns true if not false
        """

        return pwd_context.verify(password, self.t_password_hash)

    def generate_auth_token(self, expiration=600):
        """this function generates an authorization token for the client

        Keyword Arguments:
            expiration {integer} -- this is the life time for the token its measured
            in milliseconds (default: {600})

        Returns:
            dictionary -- returns a par key value describing the id of the user and
            its value (an integer)
        """

        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.t_id})

    @staticmethod
    def verify_auth_token(token):
        """[summary]

        Arguments:
            token {[type]} -- [description]
        """
        s = Serializer(secret_key)

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user_id = data['id']
        return user_id


class Category(Base):
    """this is the category table stores the user id as a one to many ralation, stores just the
    categry name, finally it serializes all its fields for the JSON end points

    Arguments:
        Base {declarative_base} --  special class that correspond to tables in the DB
    """

    __tablename__ = 'category'

    # table fields

    t_id = Column(Integer, primary_key=True)
    t_catName = Column(String(250), nullable=False, unique=True)

    # table relations

    t_userId = Column(Integer, ForeignKey('user.t_id'))
    t_relationU = relationship(User)

    @property
    def serialize(self):
        """ Return object data in a easily serializeable format"""

        return {'name': self.t_catName}


class Item(Base):
    """Item stores the item information (name and description), also stores the id of the user and
    the id of the category is part of in an one to many relationship, finally it serializes all
    its fields for the JSON end points

    Arguments:
        Base {declarative_base} --  special class that correspond to tables in the DB
    """

    __tablename__ = 'item'

    # table fields

    t_id = Column(Integer, primary_key=True)
    t_itemName = Column(String(100), nullable=False, unique=True)
    t_itemDescription = Column(String(250), nullable=False)

    # table relations

    t_userId = Column(Integer, ForeignKey('user.t_id', ondelete="CASCADE"))
    t_relationU = relationship(User)

    t_catId = Column(Integer, ForeignKey('category.t_id', ondelete="CASCADE"))
    t_relationC = relationship(Category)

    @property
    def serialize(self):
        """ Return object data in a easily serializeable format """

        return {'id': self.t_id,
                'user_id': self.t_userId,
                'category_id': self.t_catId,
                'name': self.t_itemName,
                'description': self.t_itemDescription}


engine = create_engine('sqlite:///catalogApp.db')

Base.metadata.create_all(engine)
