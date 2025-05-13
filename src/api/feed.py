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

@router.get("/", status_code=status.HTTP_200_OK)
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
            feed.append({
                "game_title": review.game_title,
                "username": review.username,
                "score": review.score,
                "description": review.description
            })

    return feed
