from typing import Dict, Optional, List, Literal
from uuid import UUID
from datetime import date, datetime
from pydantic import BaseModel, Field


class RecipeCreate(BaseModel):
    name: str = Field(..., description="Name of the recipe")
    description: Optional[str] = Field(None, description="Detailed description of the recipe")
    ingredients: Dict[str, str] = Field(..., description="Dictionary of ingredients with amounts (e.g., {'flour': '2 cups'})")
    instructions: str = Field(..., description="Step-by-step cooking instructions")
    servings: Optional[int] = Field(None, description="Number of servings this recipe makes", ge=1)
    cooking_time: Optional[int] = Field(None, description="Total cooking time in minutes", ge=1)
    complexity: Optional[Literal["easy", "medium", "hard"]] = Field(None, description="Difficulty level of the recipe")
    calories: Optional[int] = Field(None, description="Estimated calories per serving", ge=0)
    image: Optional[str] = Field(None, description="Path to the recipe image (e.g., '/images/filename.jpg')")
    tags: Optional[List[str]] = Field(None, description="List of tags for categorizing the recipe (e.g., ['vegan', 'dessert'])")
    last_cooked: Optional[date] = Field(None, description="Date when this recipe was last cooked")


class RecipeId(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the created recipe")


class Recipe(BaseModel):
    id: UUID = Field(..., description="Unique identifier of the recipe")
    name: str = Field(..., description="Name of the recipe")
    description: Optional[str] = Field(None, description="Detailed description of the recipe")
    ingredients: Dict[str, str] = Field(..., description="Dictionary of ingredients with amounts (e.g., {'flour': '2 cups'})")
    instructions: str = Field(..., description="Step-by-step cooking instructions")
    servings: Optional[int] = Field(None, description="Number of servings this recipe makes")
    cooking_time: Optional[int] = Field(None, description="Total cooking time in minutes")
    complexity: Optional[Literal["easy", "medium", "hard"]] = Field(None, description="Difficulty level of the recipe")
    calories: Optional[int] = Field(None, description="Estimated calories per serving")
    image: Optional[str] = Field(None, description="Path to the recipe image (e.g., '/images/filename.jpg')")
    tags: Optional[List[str]] = Field(None, description="List of tags for categorizing the recipe (e.g., ['vegan', 'dessert'])")
    last_cooked: Optional[date] = Field(None, description="Date when this recipe was last cooked")
    created_at: datetime = Field(..., description="Timestamp when the recipe was created")


class RecipeList(BaseModel):
    recipes: List[Recipe] = Field(..., description="List of recipes")


class ImageUploadResponse(BaseModel):
    image_path: str = Field(..., description="Path to the uploaded image that can be used in recipe creation")


class DeleteResponse(BaseModel):
    status: str = Field(..., description="Status of the delete operation")


class Healthcheck(BaseModel):
    message: str = Field(..., description="Health status message")