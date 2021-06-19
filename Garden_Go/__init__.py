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
from Garden_Go.utils.speciesNew import getSpecies,getSpeciesfromSrc,getScore

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
            access_token=authorize.create_access_token(subject=user.email, expires_time=False),
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
    user_db: models.User = db.query(models.User).filter(models.User.email == current_user).first()
    if user_db is None:
        raise HTTPException(status_code=500, detail="Bug in Database")
    user = schemas.UserBase.from_orm(user_db)
    return user


@app.delete('/user')
def del_user(authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    user_db: models.User = crud.get_user_by_email(db, current_user)
    if user_db is None:
        raise HTTPException(status_code=500, detail="Bug in Database")
    crud.delete_user(db, user_db)
    return {"msg": "User Deleted Successfully"}


@app.post('/species')
async def get_species(request:Request ,authorize: AuthJWT = Depends()):
    """
    Get all the information about a plant image
    """
    authorize.jwt_required()

    try: 
        image = await request.body() 
        pred = getSpecies(image)
        suggs = pred["suggestions"][0]

        # Construct the response Model
        resp = schemas.PlantPred()
        resp.is_plant = pred.get("is_plant",False)

        resp.pred_prob = suggs.get("probability", 0.0)
        resp.plant_name = suggs.get("plant_name","")
        resp.common_names = suggs["plant_details"].get("comman_names", [])
        resp.species = suggs["plant_details"].get("scientific_name","")
        resp.url = suggs["plant_details"].get("url","")
        resp.description = suggs["plant_details"].get("wiki_description",{"value": ""}).get("value", "")
        resp.score = getScore(resp.plant_name)

        # print(resp)

        return resp 

    except Exception as e:
        HTTPException("500",detail="Plant ID API Down")

    return None


@app.post('/plantation')
def plantation(authorize: AuthJWT = Depends()):
    """
    1. write schema in schemas.py for request, and rsponse
    2. add plantation claim points
    """
    raise NotImplementedError
