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
