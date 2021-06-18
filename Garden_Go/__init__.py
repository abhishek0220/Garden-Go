from fastapi import Depends, FastAPI
from typing import Generator
from sqlalchemy.orm import Session
from Garden_Go.Database import SessionLocal, engine
from Garden_Go.Database import models
from Garden_Go import crud, schemas

#models.Base.metadata.create_all(bind=engine)

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


@app.post("/users/", response_model=schemas.UserBase)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)
