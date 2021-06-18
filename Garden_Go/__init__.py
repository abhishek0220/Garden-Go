from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Generator
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

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
