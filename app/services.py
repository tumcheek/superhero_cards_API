from fastapi import HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from .auth.auth_bearer import JWTBearer
from .auth.auth_handler import decode_JWT
from .utils import get_password_hash, convert_user_model_to_user_schemas
from .models import User, HeroCard


def create_user(db: Session, email: str, password: str):
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

    return user


def check_user(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="Incorrect username or password")


def get_users_list(db: Session, skip, limit):
    users = db.query(User).offset(skip).limit(limit).all()
    user_schemas = []
    for user in users:
        user_schema = convert_user_model_to_user_schemas(user)
        user_schemas.append(user_schema)
    total_users = db.query(User).count()
    total_pages = (total_users + limit - 1) // limit
    current_page = (skip // limit) + 1
    result = {
        'users': user_schemas,
        'total': total_users,
        'total_pages': total_pages,
        'page': current_page
    }
    return result


def get_user_by_id(db: Session, id: int):
    user = db.query(User).filter(User.id == id).first()
    return user


def check_user_by_token(db: Session, token: str = Depends(JWTBearer())):
    decoded_token = decode_JWT(token)
    user = db.query(User).filter(User.email == decoded_token['email']).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_hero_cards_list(db: Session, skip, limit):
    hero_cards = db.query(HeroCard).offset(skip).limit(limit).all()
    total_hero_cards = db.query(HeroCard).count()
    total_pages = (total_hero_cards + limit - 1) // limit
    current_page = (skip // limit) + 1
    result = {
        'hero_cards': hero_cards,
        'total': total_hero_cards,
        'total_pages': total_pages,
        'page': current_page
    }
    return result


def get_hero_card_by_id(db: Session, id: int):
    hero_card = db.query(HeroCard).filter(HeroCard.id == id).first()
    return hero_card


def add_hero_card_to_user(db: Session, user_id: int, hero_card_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    hero_card = db.query(HeroCard).filter(HeroCard.id == hero_card_id).first()
    user.heroes.append(hero_card)
    db.add(user)
    db.commit()


def get_user_hero_cards(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user.heroes


def delete_hero_card_to_user(db: Session, user_id: int, hero_card_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    hero_card = db.query(HeroCard).filter(HeroCard.id == hero_card_id).first()
    user.heroes.remove(hero_card)
    db.add(user)
    db.commit()


def get_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} doesn't exist.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_hero_card(db: Session, hero_card_id: int):
    hero_card = get_hero_card_by_id(db, hero_card_id)
    if hero_card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hero with id {hero_card_id} not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return hero_card

