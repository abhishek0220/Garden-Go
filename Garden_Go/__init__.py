from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import pprint

from Garden_Go.Database import SessionLocal, engine
from Garden_Go.Database import models
from Garden_Go import crud, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get("/")
def index() -> str:
    return "hello world"


@app.post("/signup", response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_added = crud.create_user(db=db, user=user)
    return schemas.UserBase.from_orm(user_added)


@app.post('/login', response_model=schemas.TokenJWT)
def login(user: schemas.UserLogin, authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user and db_user.password == user.password:
        token = schemas.TokenJWT.construct(
            access_token=authorize.create_access_token(subject=user.email),
            refresh_token=authorize.create_refresh_token(subject=user.email)
        )
        return token
    else:
        raise HTTPException(status_code=401, detail="Invalid Email or password")


@app.post('/refresh')
def refresh(authorize: AuthJWT = Depends()):
    """
    follow login response type and docs here (https://indominusbyte.github.io/fastapi-jwt-auth/usage/refresh/ )
    """
    authorize.jwt_refresh_token_required()
    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(current_user)
    # No way to get the refresh token here.
    return {"access_token":new_access_token}


@app.get('/user', response_model=schemas.UserBase)
def get_user(authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    """
    get user from token follow https://indominusbyte.github.io
    """
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    user_db = db.query(models.User).filter(models.User.email == current_user).first()
    if user_db is None:
        raise HTTPException(status_code=500, detail="Bug in Database")
    
    # Create UserBase Response
    user = schemas.UserBase.construct(
        email=user_db.email,
        name=user_db.name,
        display_picture=user_db.display_picture,
        score=user_db.score
    )
    return user


@app.post('/species')
def get_species(authorize: AuthJWT = Depends()):
    """
    1. write schema in schemas.py for response, request
    2. Complete this
    """
    raise NotImplementedError


@app.post('/plantation')
def plantation(authorize: AuthJWT = Depends()):
    """
    1. write schema in schemas.py for request, and rsponse
    2. add plantation claim points
    """
    raise NotImplementedError
