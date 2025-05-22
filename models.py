from sqlalchemy.testing.suite.test_reflection import users

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Index, ForeignKey


class Users(Base):
    __tablename__ = 'users'

    id =  Column(Integer, primary_key= True, index = True)
    email = Column(String, unique= True)
    username = Column(String, unique= True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(String)


class User_info(Base):
    __tablename__ = 'info'

    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String)
    age = Column(Integer)
    marital_status = Column(String)
    is_seeking_gender = Column(String)
    seeking_age = Column(Integer)
    sports = Column(String)
    hobbies = Column(String)
    language = Column(String)
    drinking = Column(Boolean)
    smoking = Column(Boolean)
    about_you = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))




class Likes(Base):
    __tablename__ = 'interested'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,ForeignKey('users.username'))
    liked_id = Column(Integer)
    owner_id = Column(Integer, ForeignKey('users.id'))
