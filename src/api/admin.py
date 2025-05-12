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


@router.delete("/admin/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(review_id: int):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM reviews
                WHERE review.id = review_id
                """
            ),
            [{"review_id": review_id}],
        )
    pass
