from os.path import defpath

from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import session, aliased
from sqlalchemy import and_,or_
from sqlalchemy.testing.suite.test_reflection import users

from models import Likes,Users, User_info
from database import engine, SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from .auth import get_current_user


router= APIRouter()

class Info(BaseModel):
    gender: str
    age: int
    marital_status: str
    is_seeking_gender: str
    seeking_age: int
    sports: str
    hobbies: str
    language: str
    drinking: bool
    smoking: bool
    about_you: str

class SendLike(BaseModel):
    liked_id : int

class Like(BaseModel):
    user_id : list[str]
    user_info : list[Info]

class mutualUser(BaseModel):
    id: int
    name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency= Annotated[session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]



@router.post("/User_info/", status_code=status.HTTP_201_CREATED)
async def Add_Info(user: user_dependency,db: db_dependency,
                   new: Info):

    if user is None:
        raise HTTPException(status_code=401)
    new_info = User_info(**new.model_dump(),user_id = user.get('id'))
    db.add(new_info)
    db.commit()

@router.get("/recommendation")
async def read_all(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401)

    a = db.query(User_info).filter(User_info.user_id == user.get('id')).first()
    b = db.query(User_info).filter(
    and_(
        or_(
            User_info.sports == a.sports,
            User_info.age <= a.seeking_age,
            User_info.language == a.language,
            User_info.smoking == a.smoking,
            User_info.drinking == a.drinking,
            User_info.hobbies == a.hobbies),User_info.user_id != a.user_id),User_info.gender == a.is_seeking_gender,User_info.age <= a.seeking_age).all()

    return b, [u[0] for u in db.query(Users.username).filter(Users.id.in_([i.user_id for i in b])).all()]

@router.post("/sendlike/liked_id")
async def send_like(user: user_dependency, db: db_dependency, liked_id : SendLike):
    if user is None:
        raise HTTPException(status_code=401)
    a = liked_id.liked_id
    b = db.query(Users.username).filter(Users.id == a).first()
    new_like = Likes(**liked_id.model_dump(),owner_id = user.get('id'),name = b[0])
    db.add(new_like)
    db.commit()

@router.get("/mutual",response_model=list[str])
async def mutual_likes(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401)

    l1 = aliased(Likes)
    l2 = aliased(Likes)
    a=(db.query(l1.liked_id.label("mutual_user_id")).join(l2, (l1.owner_id == l2.liked_id) & (l1.liked_id == l2.owner_id)).filter(l1.owner_id == user.get('id')).subquery())
    #results = a.first()
    #b= [row.mutual_user_id for row in results]
    r = db.query(Users.username).filter(Users.id.in_(a)).all()
    return [s[0] for s in r]
@router.get("/likes", response_model=Like)
async def likes(user : user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401)

    u = db.query(Likes.owner_id).filter(Likes.liked_id == user.get('id')).all()
    a = [y[0] for y in u]

    r = db.query(Users.username).filter(Users.id.in_(a)).all()
    p = db.query(User_info).filter(User_info.user_id.in_(a)).all()

    return {
        "user_id" : [d[0] for d in r],
        "user_info" : p
    }

