from passlib.context import CryptContext
from app.schemas import UserSchema
from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def convert_user_model_to_user_schemas(user: User) -> UserSchema:
    return UserSchema(id=user.id, email=user.email)
