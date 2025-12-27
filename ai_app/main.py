from fastapi import FastAPI, HTTPException
from app.schemas import RecipeRequest, RecipeResponse
from app.core.agent import BuReAgent

app = FastAPI(
    title="BuRe Recipe Agent API",
    version="1.0.0"
)

agent = BuReAgent()


@app.post("/recipe", response_model=RecipeResponse)
def get_recipe(request: RecipeRequest):
    """
    Генерация или поиск рецепта по запросу пользователя
    """
    try:
        result = agent.invoke(request.query)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Не удалось получить рецепт"
            )

        return RecipeResponse(recipe=result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
