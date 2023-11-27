from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from starlette import status

from .models import Base
from .database import engine, Session
from .services import (create_user, check_user, get_users_list, get_user_by_id, check_user_by_token,
                       get_hero_cards_list, add_hero_card_to_user, get_user_hero_cards,
                       delete_hero_card_to_user, is_user_exist, is_hero_card_exist)
from .auth.auth_bearer import JWTBearer
from .auth.auth_handler import sign_jwt
from .schemas import UserCreateSchema, UserSchema, PaginatedUsersSchema, HeroCardIdSchema
from .utils import verify_password

Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@app.post('/users/', tags=["users"])
async def register_user(user_data: UserCreateSchema, db: Annotated[Session, Depends(get_db)]) -> UserSchema:
    user = create_user(db, email=user_data.email, password=user_data.password)
    return UserSchema(id=user.id, email=user.email)


@app.get('/users/me/', tags=["users"])
async def read_user_me(db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(JWTBearer())]):
    user = check_user_by_token(db, token)
    return UserSchema(id=user.id, email=user.email)


@app.get('/users/', response_model=PaginatedUsersSchema, tags=["users"])
async def read_users(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 10,):
    users = get_users_list(db, skip, limit)
    return PaginatedUsersSchema(**users)


@app.get('/users/{id}', response_model=UserSchema, tags=["users"])
async def read_user(id: int, db: Annotated[Session, Depends(get_db)]):

    user = get_user_by_id(db, id)
    if user is not None:
        return UserSchema(id=user.id, email=user.email)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id {id} not found",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post('/auth/token/', tags=['auth'])
async def get_token(form_data: UserCreateSchema, db: Annotated[Session, Depends(get_db)]):
    user = check_user(db, form_data.email)
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sign_jwt(user.email)


@app.get('/hero-cards/', tags=['hero-cards'])
async def read_hero_cards(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 10,):
    return get_hero_cards_list(db, skip, limit)


@app.get('/hero-cards/{id}', tags=["hero-cards"])
async def read_hero_card(id: int, db: Annotated[Session, Depends(get_db)]):
    hero_card = is_hero_card_exist(db, id)
    return hero_card


@app.get('/users/me/hero-cards/', tags=['users-hero-cards'])
def read_my_hero_cards(db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(JWTBearer())]):
    user = check_user_by_token(db, token)
    user_hero_cards = get_user_hero_cards(db, user.id)
    return user_hero_cards


@app.post('/users/me/hero-cards/', tags=['users-hero-cards'])
def add_hero_to_user(hero_card_id: HeroCardIdSchema,
                     db: Annotated[Session, Depends(get_db)],
                     token: Annotated[str, Depends(JWTBearer())]):
    user = check_user_by_token(db, token)
    hero_card = is_hero_card_exist(db, hero_card_id.hero_card_id)
    add_hero_card_to_user(db, user.id, hero_card_id.hero_card_id)
    return {'status': 'success',
            'hero_id': hero_card.id}


@app.delete('/users/me/hero-cards/{id}', tags=['users-hero-cards'])
def delete_user_card(id, db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(JWTBearer())]):
    user = check_user_by_token(db, token)
    try:
        delete_hero_card_to_user(db, user.id, id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hero with id {id} not in your list.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"status": "success", "deleted_hero_id": id}


@app.get('/users/{user_id}/hero-cards/', tags=['users-hero-cards'])
def read_user_cards(user_id: int, db: Annotated[Session, Depends(get_db)]):
    is_user_exist(db, user_id)
    user_hero_cards = get_user_hero_cards(db, user_id)
    return user_hero_cards
