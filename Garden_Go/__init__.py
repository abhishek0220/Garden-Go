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
from Garden_Go.utils.speciesNew import identify_plant

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
async def get_species(img_req: schemas.SpeciesReq, authorize: AuthJWT = Depends()):
    """
    Get all the information about a plant image
    """
    authorize.jwt_required()

    resp = {
        "is_plant": True,
        "pred_prob": 0.5240204113016891,
        "plant_name": "Spathiphyllum",
        "common_names": [
            "spath",
            "peace lilies"
        ],
        "species": "Spathiphyllum",
        "url": "https://en.wikipedia.org/wiki/Spathiphyllum",
        "description": "Spathiphyllum is a genus of about 47 species of monocotyledonous flowering plants in the family Araceae, native to tropical regions of the Americas and southeastern Asia. Certain species of Spathiphyllum are commonly known as spath or peace lilies.\nThey are evergreen herbaceous perennial plants with large leaves 12–65 cm long and 3–25 cm broad. The flowers are produced in a spadix, surrounded by a 10–30 cm long, white, yellowish, or greenish spathe. The plant does not need large amounts of light or water to survive."
    }

    '''
    try:
        # image = await request.body()
        pred = identify_plant(img_req.image)
        print(pred, "=========================================")
        suggested = pred["suggestions"][0]

        # Construct the response Model
        resp = schemas.PlantPred.construct(
            is_plant=pred.get("is_plant", False),
            pred_prob=suggested.get("probability", 0.0),
            plant_name=suggested.get("plant_name", ""),
            common_names=suggested["plant_details"].get("common_names", []),
            species=suggested["plant_details"].get("scientific_name", ""),
            url=suggested["plant_details"].get("url", ""),
            description=suggested["plant_details"].get(
                "wiki_description", {"value": ""}
            ).get("value", "")
        )
        # score = getScore(resp.plant_name)
        # print(resp)
        return resp 

    except Exception as e:
        HTTPException(500, detail=f"Plant ID API Down {e}")

    return None
    '''
    return schemas.PlantPred(**resp)


@app.post('/plantation')
def plantation(authorize: AuthJWT = Depends()):
    """
    1. write schema in schemas.py for request, and response
    2. add plantation claim points
    """
    raise NotImplementedError
