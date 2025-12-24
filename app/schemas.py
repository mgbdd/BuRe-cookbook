from typing import Dict, Optional, List, Literal
from uuid import UUID
from pydantic import BaseModel


class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: Dict[str, str]
    instructions: str
    servings: Optional[int] = None
    cooking_time: Optional[int] = None
    complexity: Optional[Literal["easy", "medium", "hard"]] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = None


class RecipeId(BaseModel):
    id: UUID


class Recipe(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    ingredients: Dict[str, str]
    instructions: str
    servings: Optional[int] = None
    cooking_time: Optional[int] = None
    complexity: Optional[Literal["easy", "medium", "hard"]] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = None


class RecipeList(BaseModel):
    recipes: List[Recipe]


class ImageUploadResponse(BaseModel):
    image_path: str


class DeleteResponse(BaseModel):
    status: str


class Healthcheck(BaseModel):
    message: str