from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import mapped_column, DeclarativeBase, relationship
from sqlalchemy import Table


class Base(DeclarativeBase):
    pass


users_heroes_table = Table(
    "users_heroes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("hero_id", ForeignKey("heroes.id")),
)


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    email = mapped_column(String, unique=True, index=True)
    hashed_password = mapped_column(String)
    heroes = relationship("HeroCard", secondary=users_heroes_table)


class HeroCard(Base):
    __tablename__ = "heroes"
    id = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name = mapped_column(String)
    gender = mapped_column(String)
    intelligence = mapped_column(Integer)
    strength = mapped_column(Integer)
    speed = mapped_column(Integer)
    durability = mapped_column(Integer)
    power = mapped_column(Integer)
    combat = mapped_column(Integer)
    img = mapped_column(String)
