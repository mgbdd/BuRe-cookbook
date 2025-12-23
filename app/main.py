from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid
import asyncio
import logging

from app.database import Base, engine, AsyncSessionLocal
from app import crud, schemas, models
from app.models import User

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recipes API")

FAKE_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    
    try:
        # Создаем таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created!")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return
    
    # Создаем тестового пользователя
    async with AsyncSessionLocal() as db:
        try:
            user_result = await db.execute(
                models.User.__table__.select().where(
                    models.User.user_id == FAKE_USER_ID
                )
            )
            user = user_result.first()
            
            if not user:
                await db.execute(
                    models.User.__table__.insert().values(
                        user_id=FAKE_USER_ID,
                        username="test_user"
                    )
                )
                await db.commit()
                logger.info("Fake user created successfully")
            else:
                logger.info("Fake user already exists")
        except Exception as e:
            logger.error(f"Error creating fake user: {e}")
            await db.rollback()

@app.get("/")
async def root():
    return {"message": "Recipes API is running"}

@app.post("/recipes", response_model=schemas.RecipeOut)
async def create_recipe(recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    db_recipe = await crud.create_recipe(db, FAKE_USER_ID, recipe)
    
    return {
        "id": db_recipe.recipe_id,
        "name": db_recipe.name,
        "description": db_recipe.description,
        "ingredients": db_recipe.ingredients,
        "instructions": db_recipe.instructions,
        "servings": db_recipe.servings,
        "cooking_time": db_recipe.cooking_time,
        "complexity": db_recipe.complexity,
        "image": None
    }

@app.get("/recipes", response_model=list[schemas.RecipeOut])
async def list_recipes(db: AsyncSession = Depends(get_db)):
    recipes = await crud.get_recipes(db, FAKE_USER_ID)
    
    result = []
    for recipe in recipes:
        result.append({
            "id": recipe.recipe_id,
            "name": recipe.name,
            "description": recipe.description,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "servings": recipe.servings,
            "cooking_time": recipe.cooking_time,
            "complexity": recipe.complexity,
            "image": None
        })
    
    return result

@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeOut)
async def get_recipe(recipe_id: UUID, db: AsyncSession = Depends(get_db)):
    recipe = await crud.get_recipe(db, recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "id": recipe.recipe_id,
        "name": recipe.name,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "servings": recipe.servings,
        "cooking_time": recipe.cooking_time,
        "complexity": recipe.complexity,
        "image": None
    }

@app.put("/recipes/{recipe_id}", response_model=schemas.RecipeOut)
async def update_recipe(recipe_id: UUID, recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    updated_recipe = await crud.update_recipe(db, recipe_id, recipe)
    
    if not updated_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return {
        "id": updated_recipe.recipe_id,
        "name": updated_recipe.name,
        "description": updated_recipe.description,
        "ingredients": updated_recipe.ingredients,
        "instructions": updated_recipe.instructions,
        "servings": updated_recipe.servings,
        "cooking_time": updated_recipe.cooking_time,
        "complexity": updated_recipe.complexity,
        "image": None
    }
@app.delete("/recipes/{recipe_id}")
async def delete_recipe(recipe_id: UUID, db: AsyncSession = Depends(get_db)):
    recipe = await crud.get_recipe(db, recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    await crud.delete_recipe(db, recipe_id)
    return {"status": "deleted"}