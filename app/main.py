from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import uuid
import logging
import os
import aiofiles
from pathlib import Path

from app.database import Base, engine, AsyncSessionLocal
from app import crud, schemas, models

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recipes API")

FAKE_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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

@app.get(
    "/",
    response_model=schemas.Healthcheck,
    summary="Health Check",
    description="Check if the API is running and healthy"
)
async def root():
    return {"message": "Recipes API is running"}

@app.post(
    "/recipes",
    response_model=schemas.RecipeId,
    summary="Create Recipe",
    description="Create a new recipe and return its unique ID",
    status_code=201
)
async def create_recipe(recipe: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    db_recipe = await crud.create_recipe(db, FAKE_USER_ID, recipe)
    
    return {
        "id": db_recipe.recipe_id
    }

@app.get(
    "/recipes",
    response_model=schemas.RecipeList,
    summary="List Recipes",
    description="Get a list of all recipes"
)
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
            "calories": recipe.calories,
            "image": recipe.image,
            "tags": recipe.tags,
            "last_cooked": recipe.last_cooked,
            "created_at": recipe.created_at
        })
    
    return {"recipes": result}

@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.Recipe,
    summary="Get Recipe",
    description="Get a specific recipe by its ID"
)
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
        "calories": recipe.calories,
        "image": recipe.image,
        "tags": recipe.tags,
        "last_cooked": recipe.last_cooked,
        "created_at": recipe.created_at
    }

@app.put(
    "/recipes/{recipe_id}",
    response_model=schemas.Recipe,
    summary="Update Recipe",
    description="Update an existing recipe by its ID"
)
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
        "calories": updated_recipe.calories,
        "image": updated_recipe.image,
        "tags": updated_recipe.tags,
        "last_cooked": updated_recipe.last_cooked,
        "created_at": updated_recipe.created_at
    }

@app.delete(
    "/recipes/{recipe_id}",
    response_model=schemas.DeleteResponse,
    summary="Delete Recipe",
    description="Delete a recipe by its ID"
)
async def delete_recipe(recipe_id: UUID, db: AsyncSession = Depends(get_db)):
    recipe = await crud.get_recipe(db, recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    await crud.delete_recipe(db, recipe_id)
    return {"status": "deleted"}

@app.post(
    "/images",
    response_model=schemas.ImageUploadResponse,
    summary="Upload Image",
    description="Upload an image file for use in recipes. Returns the path to use in the recipe's image field.",
    status_code=201
)
async def upload_image(file: UploadFile = File(..., description="Image file to upload (JPEG, PNG, etc.)")):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return {"image_path": f"/images/{unique_filename}"}

@app.get(
    "/images/{filename}",
    response_class=FileResponse,
    summary="Get Image",
    description="Retrieve an uploaded image file",
    responses={
        200: {
            "content": {
                "image/jpeg": {},
                "image/png": {},
                "image/gif": {},
                "image/webp": {}
            },
            "description": "The image file"
        },
        404: {"description": "Image not found"}
    }
)
async def get_image(filename: str):
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)