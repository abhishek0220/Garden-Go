from fastapi import Depends, FastAPI, HTTPException
from typing import Generator
from sqlalchemy.orm import Session
from Garden_Go.Database import SessionLocal, engine
from Garden_Go.Database import models
from Garden_Go import crud, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def index() -> str:
    return "hello world"


@app.post("/signup/", response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_added = crud.create_user(db=db, user=user)
    return schemas.UserBase.from_orm(user_added)
