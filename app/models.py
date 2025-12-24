import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base

from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)


class Recipe(Base):
    __tablename__ = "recipes"

    recipe_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)

    name = Column(String, nullable=False)
    instructions = Column(Text, nullable=False)
    description = Column(Text)
    servings = Column(Integer, nullable=True)
    cooking_time = Column(Integer, nullable=True)
    complexity = Column(String, nullable=True)
    calories = Column(Integer, nullable=True)
    ingredients = Column(JSONB, nullable=False, default={})
    image = Column(String, nullable=True)
    tags = Column(JSONB, nullable=True, default=[])
    last_cooked = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Ingredient(Base):
    __tablename__ = "ingredients"

    ingredient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(UUID(as_uuid=True),
                       ForeignKey("recipes.recipe_id"),
                       primary_key=True)
    ingredient_id = Column(UUID(as_uuid=True),
                           ForeignKey("ingredients.ingredient_id"),
                           primary_key=True)

    amount = Column(String, nullable=False)