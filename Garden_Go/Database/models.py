from sqlalchemy import Column, ForeignKey, Integer, String, Table, DateTime
from sqlalchemy.orm import relationship, Session, RelationshipProperty
from Garden_Go.Database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    display_picture = Column(String)
    score = Column(Integer, default=0)

    plants: RelationshipProperty = relationship("Plant")

    def save_to_db(self, db: Session) -> None:
        db.add(self)
        db.commit()
        db.refresh(self)


class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    species = Column(String)
    common_species = Column(String)
    image = Column(String)
    description = Column(String)
    score = Column(Integer)
