import datetime
import time

from fastapi import APIRouter, Depends, status, HTTPException, Query
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List
from statistics import mean

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

class WholeReview(BaseModel):
    id: int
    user_id: int
    username: str
    score: float
    text: str
    updated_at: datetime.datetime

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
    reviews: List[WholeReview] = []
    optional_reviews: List[OptionalReview] = []

class GameHistory(BaseModel):
    user_id: int
    game_id: int
    time_played: float

class GameHistoryResponse(BaseModel):
    user_id: int
    game_id: int
    time_played: float
    last_played: datetime.datetime


#Returns most recent 20 games reviewed, so people can see whats been getting reviewed recently for inspiration
@router.get("/", response_model=List[Game])
def get_recent_games(limit: int = Query(10, description="Maximum number of recent games to return")):
    start = time.time()
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT DISTINCT reviews.game_id AS id, games.game, games.genre_id, reviews.updated_at
                FROM reviews
                JOIN games ON games.id = reviews.game_id 
                WHERE reviews.published = true
                ORDER BY reviews.updated_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit}  # FIXED: Removed the list wrapper
        )
        games = []
        for row in result:
            games.append(Game(id=row.id, game=row.game, genre_id=row.genre_id))

        end = time.time()
        print(end - start)
        return games
    

@router.get("/search", response_model=List[Game])
def search_games(search: str = Query(..., description="Search term for finding games")):
    start = time.time()
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, game, genre_id
                FROM games
                WHERE game ILIKE :search
                """
            ),
            {"search": f"%{search}%"}
        )
        rows = list(result.mappings())
        print(rows)
        end = time.time()
        print(end - start)
        return rows

@router.get("/{game_id}", response_model=List[Review])
def get_reviews_for_games(
    search: str = Query("", description="Filter reviews by text content"),
    limit: int = Query(10, description="Maximum number of reviews to return")
):
    start = time.time()
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT reviews.id, reviews.score, reviews.text
                FROM games
                JOIN reviews ON reviews.game_id = games.id
                WHERE games.game ILIKE :game_name
                LIMIT :limit
                """
            ),
            {"game_name": f"%{search}%", "limit": limit} 
        )
        reviews = []
        for row in result:
            reviews.append(Review(id=row.id, score=row.score, text=row.text))
        end = time.time()
        print(end - start)
        return reviews

@router.post("/history", response_model=GameHistoryResponse, status_code=status.HTTP_200_OK)
def add_game_history(history: GameHistory):
    start = time.time()
    with db.engine.begin() as connection:
        
        # Check if the game exists
        game = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM games WHERE id = :game_id
                """
            ),
            {"game_id": history.game_id}
        ).fetchone()
        
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with ID {history.game_id} not found"
            )
        
        # Check if the user exists
        user = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM users WHERE id = :user_id
                """
            ),
            {"user_id": history.user_id}
        ).fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {history.user_id} not found"
            )
        
        # Try to insert or update the history record
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO history (user_id, game_id, time_played, last_played)
                VALUES (:user_id, :game_id, :time_played, NOW())
                ON CONFLICT (user_id, game_id) 
                DO UPDATE SET 
                    time_played = history.time_played + :time_played,
                    last_played = NOW()
                RETURNING user_id, game_id, time_played, last_played
                """
            ),
            {
                "user_id": history.user_id,
                "game_id": history.game_id,
                "time_played": history.time_played
            }
        ).fetchone()

        end = time.time()
        print(end - start)
        
        return GameHistoryResponse(
            user_id=result.user_id,
            game_id=result.game_id,
            time_played=result.time_played,
            last_played=result.last_played
        )

@router.get("/{game_id}/overview", response_model = GameOverview)
def get_game_overview(game_id: int):
    start = time.time()
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"))
        
        game = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, game as title
                FROM games 
                WHERE games.id = :game_id
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
                SELECT r.id, r.user_id, username, score, text, r.updated_at
                FROM reviews r
                JOIN users ON r.user_id = users.id
                WHERE game_id = :game_id AND published = TRUE
                ORDER BY updated_at DESC
                """
            ),
            {"game_id": game_id}
        ).fetchall()

        reviews = []
        for review in reviews_data:
            reviews.append(
                WholeReview(
                    id=review.id,
                    user_id=review.user_id,
                    username=review.username,
                    score=review.score,  
                    text=review.text,  
                    updated_at=review.updated_at, 
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

        end = time.time()
        print(end - start)
        return GameOverview(
            game_id=game.id,
            title=game.title,
            aggregate_rating=round(aggregate_rating, 2),
            total_playtime=total_playtime,
            reviews=reviews,
            optional_reviews=optional_reviews
        )
