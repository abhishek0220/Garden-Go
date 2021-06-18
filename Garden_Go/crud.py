from sqlalchemy.orm import Session
from Garden_Go.Database import models
from Garden_Go import schemas


def create_user(db: Session, user: schemas.UserCreate) -> None:
    db_user = models.User(**user.dict())
    db_user.save_to_db(db)
