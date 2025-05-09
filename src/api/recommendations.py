from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/review",
    tags=["review"],
    dependencies=[Depends(auth.get_api_key)],
)

class Reviews(BaseModel):
    user_id: int
    game_id: int
    score: int
    description: str


class OptionalReviews(BaseModel):
    aspect_to_review: str
    optional_rating: int

class ReviewCreateResponse(BaseModel):
    review_id: int

@router.post("/review", response_model=ReviewCreateResponse)
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

@router.post("/review/{review_id}/optional", status_code=status.HTTP_204_NO_CONTENT)
def optional_review(review_id: int, optional: OptionalReviews):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO optional_reviews (review_name, optional_rating, review_id)
                VALUES (:review_name, :optional_rating, :review_id)
                RETURNING id
                """
            ),
            [{"review_name": optional.aspect_to_review, "optional_rating": optional.optional_rating, "review_id": review_id}],
        )
    pass

@router.post("/Recommendation", status_code=status.HTTP_204_NO_CONTENT)
def game_recommendations(user_id: int):
    with db.engine.begin() as connection:
        genres = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.genre_id AS genre_id
                FROM history
                JOIN games on history.game_id = games.game_id
                WHERE user_id = :user_id
                ORDER BY last_played, time_played
                LIMIT 5
                """
            ),
            [{"user_id": user_id}],
        )

        genres = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.genre_id AS genre_id
                FROM history
                JOIN games on history.game_id = games.game_id
                WHERE user_id = :user_id
                ORDER BY last_played, time_played
                LIMIT 5
                """
            ),
            [{"user_id": user_id}],
        )



    pass

@router.post("/review/{review_id}/publish", status_code=status.HTTP_204_NO_CONTENT)
def post_review(review_id: int):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE reviews
                SET published = True
                WHERE id = :review_id
                """
            ),
            {"review_id": review_id}
        )
    pass