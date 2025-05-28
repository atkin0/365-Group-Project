import datetime
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[Depends(auth.get_api_key)],
)

class Game(BaseModel):
    id: int
    game: str
    genre_id: int

class Review(BaseModel):
    id: int
    score: int
    text: str

class Comment(BaseModel):
    comment_id: int
    user_id: int
    username: str
    text: str
    updated_at: datetime.datetime

class WholeReview(BaseModel):
    id: int
    user_id: int
    username: str
    score: float
    text: str
    updated_at: datetime.datetime
    comments: List[Comment] = []

class OptionalReview(BaseModel):
    id: int
    review_name: str
    optional_rating: int
    review_id: int
    updated_at: datetime.datetime

class GameOverview(BaseModel):
    game_id: int
    title: str
    aggregate_rating: float
    total_playtime: int = 0
    reviews: List[Review] = []
    optional_reviews: List[OptionalReview] = []


#Returns most recent 20 games reviewed, so people can see whats been getting reviewed recently for inspiration
@router.get("/", response_model=List[Game])
def get_recent_games():
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT DISTINCT ON (reviews.game_id) reviews.game_id AS id, games.game, games.genre_id
                FROM reviews
                JOIN games ON games.id = reviews.game_id 
                WHERE reviews.published = true
                ORDER BY reviews.game_id, reviews.updated_at DESC
                LIMIT 20
                """
            )
        )
        rows = list(result.mappings())
        print(rows)
        return rows
    

@router.get("/search",response_model=List[Game])
def search_games(search: str):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, game, genre_id
                FROM games
                WHERE game ILIKE :search
                """
            ),
            [{"search": f"%{search}%"}]
        )
        rows = list(result.mappings())
        print(rows)
        return rows

@router.get("/{game_id}",response_model=List[Review])
def get_reviews_for_games(search: str):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT reviews.id, reviews.score, reviews.text
                FROM games
                JOIN reviews ON reviews.game_id = games.id
                WHERE games.game ILIKE :search
                """
            ),
            [{"search": f"%{search}%"}]
        )
        rows = list(result.mappings())
        print(rows)
        return rows


@router.get("/{game_id}/overview", response_model = GameOverview)
def get_game_overview(game_id: int):
    with db.engine.begin() as connection:
        game = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, title FROM games WHERE id = :game_id
                """
            ),
            {"game_id": game_id}
        ).fetchone()
    
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with ID {game_id} not found"
            )
        reviews_data = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, user_id, username, score, text, updated_at
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE game_id = :game_id AND published = TRUE
                ORDER BY updated_at DESC
                """
            ),
            {"game_id": game_id}
        ).fetchall()

        reviews = []
        for review in reviews_data:
            comments_data = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT c.comment_id, c.user_id, u.username, c.text, c.updated_at
                    FROM comments c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.review_id = :review_id
                    ORDER BY c.updated_at ASC
                    """
                ),
                {"review_id": review.id}
            ).fetchall()
            comments = [
                Comment(
                    comment_id=comment.comment_id,
                    user_id=comment.user_id,
                    username=comment.username,
                    text=comment.text,
                    updated_at=comment.updated_at
                ) for comment in comments_data
            ]
            reviews.append(
                Review(
                    id=review.id,
                    user_id=review.user_id,
                    username=review.username,
                    score=review.score,  
                    text=review.text,  
                    updated_at=review.updated_at, 
                    comments=comments
                )
            )
        optional_reviews_data = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT o.id, o.review_id, o.review_name, o.optional_rating, o.updated_at
                    FROM optional_reviews o
                    JOIN reviews r ON o.review_id = r.id
                    WHERE r.game_id = :game_id AND r.published = TRUE
                    ORDER BY o.updated_at DESC
                    """
                ),
                {"game_id": game_id}
            ).fetchall()
        optional_reviews = [
            OptionalReview(
                id=opt_review.id,
                review_name=opt_review.review_name,
                optional_rating=opt_review.optional_rating,
                review_id=opt_review.review_id,
                updated_at=opt_review.updated_at
            ) for opt_review in optional_reviews_data
        ]
        total_playtime_result = connection.execute(
            sqlalchemy.text(
                """
                SELECT COALESCE(SUM(time_played), 0) as total_playtime
                FROM history
                WHERE game_id = :game_id
                """
            ),
            {"game_id": game_id}
        ).fetchone()
        if total_playtime_result is None:
            total_playtime = 0
        else:
            total_playtime = int(total_playtime_result.total_playtime)
        aggregate_rating = 0
        if reviews:
            aggregate_rating = mean([review.score for review in reviews])
        return GameOverview(
            game_id=game.id,
            title=game.title,
            aggregate_rating=round(aggregate_rating, 2),
            total_playtime=total_playtime,
            reviews=reviews,
            optional_reviews=optional_reviews
        ) 
