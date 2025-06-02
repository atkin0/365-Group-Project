from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    dependencies=[Depends(auth.get_api_key)],
)

class Reviews(BaseModel):
    user_id: int
    game_id: int
    score: int
    text: str

class OptionalReviews(BaseModel):
    aspect_to_review: str
    optional_rating: int

class ReviewCreateResponse(BaseModel):
    review_id: int

class PostCommentResponse(BaseModel):
    comment_id: int

class Comment(BaseModel):
    username: str
    text: str

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
            [{"user_id": review.user_id, "score": review.score, "text": review.text, "game_id": review.game_id}],
        ).scalar_one()
    return ReviewCreateResponse(review_id=result)

@router.post("/{review_id}/optional", status_code=status.HTTP_204_NO_CONTENT)
def optional_review(review_id: int, optional: OptionalReviews):
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": review_id}).first():
            raise HTTPException(status_code=404, detail="Review doesn't exist")

        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO optional_reviews (review_name, optional_rating, review_id, updated_at)
                VALUES (:review_name, :optional_rating, :review_id, NOW())
                ON CONFLICT (review_name, review_id)
                DO UPDATE SET 
                optional_rating = :optional_rating, updated_at = NOW()
                RETURNING id
                """
            ),
            [{"review_name": optional.aspect_to_review, "optional_rating": optional.optional_rating, "review_id": review_id}],
        ).scalar_one()

    return ReviewCreateResponse(review_id=result)


@router.patch("/{review_id}/publish", status_code=status.HTTP_204_NO_CONTENT)
def post_review(review_id: int):
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": review_id}).first():
            raise HTTPException(status_code=404, detail="Review doesn't exist")

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

@router.patch("/{review_id}/edit", status_code=status.HTTP_204_NO_CONTENT)
def patch_review(review_id: int, review: Reviews):
    with db.engine.begin() as connection:

        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": review_id}).first():
            raise HTTPException(status_code=404, detail="Review doesn't exist")

        connection.execute(
            sqlalchemy.text(
                """
                UPDATE reviews 
                SET user_id = :user_id, score = :score, text = :text, game_id = :game_id, updated_at = NOW(), published = False
                WHERE id = :review_id
                """
            ),
            {"review_id": review_id, "user_id": review.user_id, "score": review.score, "text": review.text, "game_id": review.game_id}
        )
    pass

@router.post("/{review_id}/comments", status_code=status.HTTP_200_OK, response_model=PostCommentResponse)
def post_comment(review_id: int, user_id: int, comment: str):
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": review_id}).first():
            raise HTTPException(status_code=404, detail="Review doesn't exist")

        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO comments (review_id, user_id, text)
                VALUES (:review_id, :user_id, :text)
                RETURNING comment_id
                """
            ),
            {
                "review_id": review_id,
                "user_id": user_id,
                "text": comment,
            }
        ).scalar_one()

        return PostCommentResponse(comment_id=result)

@router.get("/{review_id}/comments", status_code=status.HTTP_200_OK, response_model=List[Comment])
def get_comments(review_id: int, limit: int):
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": review_id}).first():
            raise HTTPException(status_code=404, detail="Review doesn't exist")

        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT username, text 
                FROM comments
                JOIN users on comments.user_id = users.id
                WHERE review_id = :review_id
                LIMIT :limit
                """
            ),
            {
                "review_id": review_id,
                "limit": limit
            }
        ).fetchall()

    comments: List[Comment] = []

    for r in results:
        comments.append(Comment(username=r.username, text=r.text))

    return comments