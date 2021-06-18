from datetime import datetime

from pydantic import BaseModel, validator
from hashlib import md5


class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    password: str

    @validator('password', pre=True)
    def pw_creation(cls, v: str):
        if len(v) < 5:
            raise ValueError("Password too short")
        hashed_pw = md5(v.encode()).hexdigest()
        return hashed_pw


sample_user = {
    "name": "Abhishek",
    "email": "2018ucs0087@iitjammu.ac.in",
    "password": "123456",
    "dob": (20, 2, 2000)
}
