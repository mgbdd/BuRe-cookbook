from pydantic import BaseModel
from typing import Optional
from app.core.utils.recipe_model import Recipe


class RecipeRequest(BaseModel):
    query: str


class RecipeResponse(BaseModel):
    recipe: Optional[Recipe]
