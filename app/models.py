from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    email = mapped_column(String, unique=True, index=True)
    hashed_password = mapped_column(String)
