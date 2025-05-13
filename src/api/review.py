from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
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

class PostCommentResponse(BaseModel):
    comment_id: int

@router.post("/", response_model=ReviewCreateResponse)
def send_review(review: Reviews):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO reviews (user_id, score, text, game_id, updated_at)
                VALUES (:user_id, :score, :text, :game_id, NOW())
                RETURNING id
                """
            ),
            [{"user_id": review.user_id, "score": review.score, "text": review.description, "game_id": review.game_id}],
        ).scalar_one()
    return ReviewCreateResponse(review_id=result)

@router.post("/{review_id}/optional", status_code=status.HTTP_204_NO_CONTENT)
def optional_review(review_id: int, optional: OptionalReviews):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO optional_reviews (review_name, optional_rating, review_id, updated_at)
                VALUES (:review_name, :optional_rating, :review_id, NOW())
                RETURNING id
                """
            ),
            [{"review_name": optional.aspect_to_review, "optional_rating": optional.optional_rating, "review_id": review_id}],
        ).scalar_one()
    return ReviewCreateResponse(review_id=result)
    pass

@router.post("/{review_id}/publish", status_code=status.HTTP_204_NO_CONTENT)
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

@router.post("/{review_id}/edit", status_code=status.HTTP_204_NO_CONTENT)
def patch_review(review_id: int, review: Reviews):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE reviews 
                SET user_id = :user_id, score = :score, text = :text, game_id = :game_id, updated_at = NOW(), published = False
                WHERE id = :review_id
                """
            ),
            {"review_id": review_id, "user_id": review.user_id, "score": review.score, "text": review.description, "game_id": review.game_id}
        )
    pass

@router.post("/{review_id}/edit/optional", status_code=status.HTTP_204_NO_CONTENT)
def patch_optional_review(review_id: int, optional: OptionalReviews):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE optional_reviews 
                SET review_name = :review_name, optional_rating = :optional_rating, updated_at = NOW()
                WHERE id = :review_id
                """
            ),
            {"review_id": review_id, "review_name": optional.aspect_to_review, "optional_rating": optional.optional_rating}
        )
    pass

@router.post("/{review_id}/comments", status_code=status.HTTP_200_OK, response_model=PostCommentResponse)
def post_comment(review_id: int, user_id: int, comment: str):
    with db.engine.begin() as connection:
        comment_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO comments (review_id, user_id, text)
                VALUES (:review_id, :user_id, :text)
                RETURNING id
                """
            ),
            {
                "review_id": review_id,
                "user_id": user_id,
                "text": comment,
            }
        )

        return PostCommentResponse(comment_id=comment_id)