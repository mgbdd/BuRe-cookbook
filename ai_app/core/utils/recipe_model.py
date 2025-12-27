from pydantic import BaseModel, Field
from typing import Dict

class Recipe(BaseModel):
    name: str = Field(description="Название блюда")
    description: str = Field(description="Описание блюда")
    ingredients: Dict[str, str] = Field(description="Словарь ингредиентов, ингредиент : количество")
    instructions: str = Field(description="Пошаговый рецепт")
    servings: int = Field(description="Количество порций")
    cooking_time: int = Field(description="Время приготовления в минутах")
    complexity: int = Field(description="Сложность приготовления от 1 до 5") 
