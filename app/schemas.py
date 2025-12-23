from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel


class IngredientIn(BaseModel):
    name: str
    amount: str


class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: Dict[str, str]
    instructions: str
    servings: int = 1
    cooking_time: int
    complexity: int = 1


class RecipeOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    ingredients: Dict[str, str]
    instructions: str
    servings: int
    cooking_time: int
    complexity: int
    image: Optional[str] = None