from typing import Annotated
from fastapi import FastAPI,Depends, HTTPException
from starlette import status

from .models import Base
from .database import engine, Session
from .services import create_user, check_user, get_users_list, get_user_by_id, is_user_exist
from .auth.auth_bearer import JWTBearer
from .auth.auth_handler import sign_jwt
from .schemas import UserCreateSchema, UserSchema, PaginatedUsersSchema
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
    user = is_user_exist(db, token)
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




