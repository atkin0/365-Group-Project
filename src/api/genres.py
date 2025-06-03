import time

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/genres",
    tags=["genres"],
    dependencies=[Depends(auth.get_api_key)],
)

class GenreCreate(BaseModel):
    genre: str

class GenreCreateResponse(BaseModel):
    genre_id: int

class Genre(BaseModel):
    genre: str


@router.post("/", response_model=GenreCreateResponse, status_code=status.HTTP_200_OK)
def new_genre(genre_create: GenreCreate):
    start = time.time()
    with db.engine.begin() as connection:
        genre_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO genres (genre)
                VALUES (:genre)
                ON CONFLICT (genre)
                DO UPDATE SET genre = :genre
                RETURNING id
                """
            ),
            {"genre": genre_create.genre}
        ).scalar_one()

        end = time.time()
        print(end - start)

        return GenreCreateResponse(genre_id=genre_id)


@router.get("/", response_model=List[Genre], status_code=status.HTTP_200_OK)
def all_genres():
    start = time.time()
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT genre from genres
                """
            )
        ).fetchall()

    genres = []
    for r in results:
        genres.append(Genre(genre=r.genre))

    end = time.time()
    print(end - start)
    return genres
