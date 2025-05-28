from typing import List

from fastapi import APIRouter, Depends, status
import sqlalchemy
from pydantic import BaseModel
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/feed",
    tags=["feed"],
    dependencies=[Depends(auth.get_api_key)],
)

class FeedItem(BaseModel):
    game_title: str
    username: str
    score: int
    description: str

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=List[FeedItem])
def get_feed(user_id: int):
    feed = []

    with db.engine.begin() as connection:
        reviews = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.name AS game_title, users.username AS username, reviews.score AS score, reviews.text AS description
                FROM reviews
                JOIN games on reviews.game_id = games.id
                JOIN users on reviews.user_id = users.id
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
        ).fetchall()

    for review in reviews:
        feed.append(
            FeedItem(
                game_title=review.game_title,
                username=review.username,
                score=review.score,
                description=review.description
            )
        )

    return feed
