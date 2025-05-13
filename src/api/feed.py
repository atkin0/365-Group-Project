from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/feed",
    tags=["feed"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/", response_model=ReviewCreateResponse)
def send_review(review: Reviews):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO reviews (user_id, score, text, game_id)
                VALUES (:user_id, :score, :text, :game_id)
                RETURNING id
                """
            ),
            [{"user_id": review.user_id, "score": review.score, "text": review.description, "game_id": review.game_id}],
        ).scalar_one()
    return ReviewCreateResponse(review_id=result)
