from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
import sqlalchemy
from pydantic import BaseModel
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/feed",
    tags=["feed"],
    dependencies=[Depends(auth.get_api_key)],
)

class OptionalReview(BaseModel):
    aspect: str
    score: int

class FeedItem(BaseModel):
    game_title: str
    username: str
    score: int
    description: str
    optional_reviews: List[OptionalReview]



@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=List[FeedItem])
def get_feed(user_id: int):

    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")
        reviews = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.name AS game_title, users.username AS username, reviews.score AS score, reviews.text AS description, reviews.id AS review_id
                FROM reviews
                JOIN games ON reviews.game_id = games.id
                JOIN users ON reviews.user_id = users.id
                WHERE EXISTS (
                    SELECT 1 FROM friends
                    WHERE friends.user_adding_id = :user_id
                    AND friends.user_added_id = reviews.user_id
                )
                AND NOW() - reviews.updated_at < INTERVAL '30 days'
                LIMIT 10
                """
            ),
            {
                "user_id": user_id,
            },
        )

        feed = []
        for review in reviews:
            optional_reviews = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT review_name, optional_rating
                    FROM optional_reviews
                    WHERE review_id = :review_id
                    """
                ),
                {
                    "review_id": review.review_id,
                }
            )

            optional_reviews = [OptionalReview(aspect=o_r.review_name, score=o_r.optional_rating) for o_r in optional_reviews]

            feed.append(
                FeedItem(
                    game_title=review.game_title,
                    username=review.username,
                    score=review.score,
                    description=review.description,
                    optional_reviews=optional_reviews
                )
            )
        return feed
