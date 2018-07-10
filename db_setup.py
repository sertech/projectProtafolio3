from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

import random, string

Base = declarative_base()

# secret key generation
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

class User(Base):
    __tablename__ = 'user'
    t_id = Column(Integer, primary_key=True)
    t_name = Column(String(250), nullable=False)
    t_email = Column(String(250), nullable=False)
    t_picture = Column(String(250))
    t_password_hash = Column(String(64))

    def hash_password(self, password):
        self.t_password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.t_password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in = expiration)
        ''' s = Serializer(Q3OP26CF1F4PKOQ0M8V5INWCXG8VVO8K, expires_in = 600)'''
        '''
        >>> s.dumps({'id': 20})
        b'eyJhbGciOiJIUzI1NiIsImlhdCI6MTUzMDkwODg2NCwiZXhwIjoxNTMwOTE0ODY0fQ.eyJpZCI6MjB9.Njfbsv30CM1dj5jig18d2R2OvDJ_w_7hZjHeJaHbjCE' 

        >>> s.loads(b'eyJhbGciOiJIUzI1NiIsImlhdCI6MTUzMDkwODg2NCwiZXhwIjoxNTMwOTE0ODY0fQ.eyJpZCI6MjB9.Njfbsv30CM1dj5jig18d2R2OvDJ_w_7hZjHeJaHbjCE')
        {'id': 20}
        '''
        return s.dumps({'id': self.t_id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        # s = Serializer(Q3OP26CF1F4PKOQ0M8V5INWCXG8VVO8K)
        try:
            data = s.loads(token)
            # data = s.loads(b'eyJhbGciOiJIUzI1NiIsImlhdCI6MTUzMDkwODg2NCwiZXhwIjoxNTMwOTE0ODY0fQ.eyJpZCI6MjB9.Njfbsv30CM1dj5jig18d2R2OvDJ_w_7hZjHeJaHbjCE')
            # data = {'id': 20}
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        
        user_id = data['id']
        return user_id



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
    def serialize(self):
        """ Return object data in a easily serializeable format """
        return {
            'id': self.t_id,
            'name': self.t_itemName,
            'description': self.t_itemDescription
        }

engine = create_engine('sqlite:///catalogApp.db')

Base.metadata.create_all(engine)

''' Serializer process

>>> from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
>>> import random, string
>>> secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
>>> print(secret_key)
AIQ653APKWNWX166WZ4C1I6WQ5M7QF30
>>> print(secret_key)
AIQ653APKWNWX166WZ4C1I6WQ5M7QF30
>>> s = Serializer(secret_key, expires_in = 123456)
>>> s.dumps({'id': 123})
b'eyJhbGciOiJIUzI1NiIsImlhdCI6MTUzMDkxMDMwOCwiZXhwIjoxNTMxMDMzNzY0fQ.eyJpZCI6MTIzfQ.zqt9OwhJcL4J9wROmrFpuGeJcuUUEcWQ0cXmtofpxGA'
>>> s2 = Serializer(secret_key)
>>> data = s2.loads(b'eyJhbGciOiJIUzI1NiIsImlhdCI6MTUzMDkxMDMwOCwiZXhwIjoxNTMxMDMzNzY0fQ.eyJpZCI6MTIzfQ.zqt9OwhJcL4J9wROmrFpuGeJcuUUEcWQ0cXmtofpxGA')
>>> print(data)
{'id': 123}
>>> 


'''