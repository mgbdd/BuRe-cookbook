from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4

from app import models, schemas


async def get_or_create_ingredient(db: AsyncSession, name: str):
    result = await db.execute(
        select(models.Ingredient).where(models.Ingredient.name == name)
    )
    ingredient = result.scalar_one_or_none()
    
    if ingredient:
        return ingredient

    ingredient = models.Ingredient(
        ingredient_id=uuid4(),
        name=name
    )
    db.add(ingredient)
    await db.commit()
    return ingredient


async def create_recipe(db: AsyncSession, user_id, recipe: schemas.RecipeCreate):
    # Создаем рецепт
    recipe_id = uuid4()
    db_recipe = models.Recipe(
        recipe_id=recipe_id,
        user_id=user_id,
        name=recipe.name,
        description=recipe.description,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        servings=recipe.servings,
        cooking_time=recipe.cooking_time,
        complexity=recipe.complexity,
        calories=recipe.calories,
        image=recipe.image,
        tags=recipe.tags if recipe.tags else [],
        last_cooked=recipe.last_cooked
    )
    db.add(db_recipe)
    
    await db.commit()
    await db.refresh(db_recipe)
    
    return db_recipe


async def get_recipes(db: AsyncSession, user_id):
    # Получаем рецепты пользователя
    recipes_result = await db.execute(
        select(models.Recipe).where(models.Recipe.user_id == user_id)
    )
    recipes = recipes_result.scalars().all()
    
    return recipes


async def get_recipe(db: AsyncSession, recipe_id):
    # Получаем рецепт
    recipe_result = await db.execute(
        select(models.Recipe).where(models.Recipe.recipe_id == recipe_id)
    )
    recipe = recipe_result.scalar_one_or_none()
    
    return recipe


async def delete_recipe(db: AsyncSession, recipe_id):
    # Удаляем связи с ингредиентами
    await db.execute(
        models.Recipe.__table__.delete().where(
            models.Recipe.recipe_id == recipe_id
        )
    )
    await db.commit()

async def update_recipe(db: AsyncSession, recipe_id, recipe_update: schemas.RecipeCreate):
    # Получаем рецепт
    recipe_result = await db.execute(
        select(models.Recipe).where(models.Recipe.recipe_id == recipe_id)
    )
    recipe = recipe_result.scalar_one_or_none()
    
    if not recipe:
        return None
    
    # Обновляем поля
    for key, value in recipe_update.dict().items():
        setattr(recipe, key, value)
    
    await db.commit()
    await db.refresh(recipe)
    
    return recipe