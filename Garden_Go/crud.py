from sqlalchemy.orm import Session
from Garden_Go.Database import models
from Garden_Go import schemas
from Garden_Go.utils import basic


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    user.score = 0
    public_url = basic.upload_user_image(user)
    user.display_picture = public_url
    user.email = user.email.lower()
    db_user = models.User(**user.dict())
    db_user.save_to_db(db)
    return db_user


def delete_user(db: Session, user: models.User):
    basic.del_user_image(user)
    db.delete(user)
    db.commit()
