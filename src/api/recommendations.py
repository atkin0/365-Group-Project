import time

from fastapi import APIRouter, Depends, status, HTTPException
from collections import defaultdict
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/recommendation",
    tags=["recommendation"],
    dependencies=[Depends(auth.get_api_key)],
)

class Recommendation(BaseModel):
    game_name: str
    score: float
    reviews: List[str]

class GameRanked(BaseModel):
    game_id: int
    score: float

@router.get("/{user_id}", response_model=List[Recommendation])
def popular_recommendations(user_id: int):
    start = time.time()
    with db.engine.begin() as connection:

        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        genres_recent = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.genre_id AS genre_id
                FROM history
                JOIN games on history.game_id = games.id
                WHERE user_id = :user_id
                ORDER BY last_played DESC
                LIMIT 10
                """
            ),
            [{"user_id": user_id}],
        ).fetchall()

        genres_most = connection.execute(
            sqlalchemy.text(
                """
                SELECT games.genre_id AS genre_id
                FROM history
                JOIN games on history.game_id = games.id
                WHERE user_id = :user_id
                ORDER BY time_played DESC
                LIMIT 10
                """
            ),
            [{"user_id": user_id}],
        ).fetchall()

        genres_multi = defaultdict(lambda: 1)

        #valuing most played genres over recent genres
        multiplier = 1.2
        for genre in genres_most:
            genres_multi[genre.genre_id] *= multiplier
            multiplier -= 0.2

        multiplier = 1.1
        for genre in genres_recent:
            genres_multi[genre.genre_id] *= multiplier
            multiplier -= 0.1

        friend_games = connection.execute(
            sqlalchemy.text(
                """
                SELECT reviews.game_id, games.genre_id, AVG(reviews.score) as avg_score
                FROM reviews
                JOIN games on reviews.game_id = games.id
                WHERE EXISTS (
                    SELECT 1 FROM friends
                    WHERE friends.user_adding_id = :user_id
                    AND friends.user_added_id = reviews.user_id
                )
                AND NOW() - reviews.updated_at < INTERVAL '30 days'
                GROUP BY reviews.game_id, games.genre_id
                ORDER BY avg_score DESC
                LIMIT 10
                """
            ),
            [{"user_id": user_id}],
        ).fetchall()

        top_games = connection.execute(
            sqlalchemy.text(
                """
                SELECT reviews.game_id, games.genre_id, AVG(reviews.score) as avg_score
                FROM reviews
                JOIN games on reviews.game_id = games.id
                WHERE NOW() - reviews.updated_at < INTERVAL '30 days'
                GROUP BY reviews.game_id, games.genre_id
                HAVING COUNT(reviews.score) >= 1
                ORDER BY avg_score DESC
                LIMIT 10
                """
            ),
            [{"user_id": user_id}],
        ).fetchall()

    games_scores = {}
    for game in friend_games:
        games_scores[game.game_id] = float(game.avg_score) * genres_multi[game.genre_id]
    for game in top_games:
        if game.game_id in games_scores:
            games_scores[game.game_id] *= genres_multi[game.genre_id]
        else:
            games_scores[game.game_id] = float(game.avg_score) * genres_multi[game.genre_id]

    games_list: List[GameRanked] = []
    for game_id in games_scores:
        games_list.append(GameRanked(game_id=game_id, score=games_scores[game_id]))
    games_list.sort(key=lambda game: game.score, reverse=True)

    games = get_recommended_games(user_id=user_id, games_list=games_list)
    end = time.time()
    print(end - start)
    return games



def get_recommended_games(user_id, games_list: List[GameRanked]):

    recommendations: List[Recommendation] = []
    with db.engine.begin() as connection:
        for game in games_list:
            if not connection.execute(
                    sqlalchemy.text("SELECT 1 FROM games where id = :id"),
                    {"id": game.game_id}).first():
                raise HTTPException(status_code=404, detail="Game doesn't exist")

            game_name = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT game
                    FROM games
                    WHERE id = :id
                    """
                ),
                {"id": game.game_id}
            ).scalar_one()

            score = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT AVG(score) as avg_score
                    FROM reviews
                    WHERE game_id = :game_id
                    GROUP BY game_id
                    """
                ),
                {
                    "game_id": game.game_id,
                }
            ).scalar_one_or_none()

            friend_reviews = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT text
                    FROM reviews
                    WHERE game_id = :game_id
                    AND EXISTS (
                        SELECT 1 FROM friends
                        WHERE friends.user_adding_id = :user_id
                        AND friends.user_added_id = reviews.user_id
                    )
                    ORDER BY updated_at DESC
                    LIMIT 3
                    """
                ),
                {
                    "user_id": user_id,
                    "game_id": game.game_id,
                },
            ).fetchall()

            regular_reviews = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT text
                    FROM reviews
                    WHERE game_id = :game_id
                    AND NOT EXISTS (
                        SELECT 1 FROM friends
                        WHERE friends.user_adding_id = :user_id
                        AND friends.user_added_id = reviews.user_id
                    )
                    ORDER BY updated_at DESC
                    LIMIT 3
                    """
                ),
                {
                    "user_id": user_id,
                    "game_id": game.game_id,
                },
            ).fetchall()

            reviews = []

            for review in regular_reviews:
                reviews.append(review.text)
            for review in friend_reviews:
                reviews.append(review.text)

            recommendations.append(Recommendation(game_name=game_name, score=score, reviews=reviews))

    return recommendations
