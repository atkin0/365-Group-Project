import time

from fastapi import APIRouter, Depends, status, HTTPException, Query
from pydantic import BaseModel, Field, constr
import sqlalchemy
from src.api import auth
from src import database as db
from typing import List
from datetime import datetime

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
    dependencies=[Depends(auth.get_api_key)],
)

class Reviews(BaseModel):
    user_id: int
    game_id: int
    score: int = Field(..., ge=1, le=10, description="Rating must be between 1 and 10")
    text: str = Field(..., max_length=500, description="Review text limited to 500 characters")

class OptionalReviews(BaseModel):
    aspect_to_review: str
    optional_rating: int = Field(..., ge=1, le=10, description="Rating must be between 1 and 10")

class ReviewCreateResponse(BaseModel):
    review_id: int

class GetReview(BaseModel):
    username: str
    game: str
    score: int
    text: str
    updated_at: datetime

class GetOptionalReview(BaseModel):
    username: str
    game: str
    aspectToReview: str
    score: int
    updated_at: datetime

class PostCommentResponse(BaseModel):
    comment_id: int

class Comment(BaseModel):
    username: str
    text: str

class CommentCreate(BaseModel):
    review_id: int
    user_id: int
    comment: str = Field(..., max_length=500, description="Comment text limited to 500 characters")

class ReviewPublishResponse(BaseModel):
    review_id: int
    published_at: datetime
    status: str

class ReviewUpdateResponse(BaseModel):
    review_id: int
    updated_at: datetime
    changes_applied: bool

@router.post("/", response_model=ReviewCreateResponse)
def send_review(review: Reviews):
    start = time.time()
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO reviews (user_id, score, text, game_id, updated_at)
                VALUES (:user_id, :score, :text, :game_id, NOW())
                RETURNING id
                """
            ),
            {"user_id": review.user_id, "score": review.score, "text": review.text, "game_id": review.game_id},
        ).scalar_one()
    end = time.time()
    print(end - start)
    return ReviewCreateResponse(review_id=result)

#review_id links the optional_review and required review
@router.post("/{review_id}/optional")
def optional_review(review_id: int, optional: OptionalReviews):
    """
    Optional reviews for reviewing different aspects of a game. Each review can have multiple optional reviews extending.
    """
    start = time.time()
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
                RETURNING id
                """
            ),
            {"review_name": optional.aspect_to_review, "optional_rating": optional.optional_rating, "review_id": review_id},
        ).scalar_one()
    end = time.time()
    print(end - start)
    return ReviewCreateResponse(review_id=result)


@router.patch("/{review_id}/publish")
def post_review(review_id: int):
    start = time.time()
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": review_id}).first():
            raise HTTPException(status_code=404, detail="Review doesn't exist")
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE reviews
                SET published = TRUE
                WHERE id = :review_id
                """
            ),
            {"review_id": review_id}
        )
        current_time = connection.execute(
            sqlalchemy.text("SELECT NOW() as timestamp")
        ).scalar_one()
    end = time.time()
    print(end - start)
    return ReviewPublishResponse(
        review_id=review_id,
        published_at=current_time,
        status="Review successfully published"
    )

@router.patch("/{review_id}/edit")
def patch_review(review_id: int, review: Reviews):
    start = time.time()
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
        current_time = connection.execute(
            sqlalchemy.text("SELECT NOW() as timestamp")
        ).scalar_one()
        
    end = time.time()
    print(end - start)
    return ReviewUpdateResponse(
        review_id=review_id,
        updated_at=current_time,
        changes_applied=True
    )

@router.get("/{review_id}/get", response_model=GetReview)
def get_review_from_id(review_id: int):
    start = time.time()
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username, games.game, score, text, updated_at
                FROM reviews
                JOIN users ON users.id = reviews.user_id
                JOIN games ON games.id = reviews.game_id
                WHERE reviews.id = :review_id AND reviews.published = TRUE
                """
            ),
            {"review_id": review_id}
        ).mappings().fetchone()

    print(result)
    if not result:
        raise HTTPException(status_code=404, detail="Invalid Review ID")
    end = time.time()
    print(end - start)
    return(GetReview(username=result["username"], game=result["game"],score=result["score"],text=result["text"],updated_at=result["updated_at"]))

#Pass in the review ID to get the optional reviews linked to it
@router.get("/{review_id}/get/optional", response_model=List[GetOptionalReview])
def get_optional_review_from_id(review_id: int):
    with db.engine.begin() as connection:
        if not connection.execute(
                    sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                    {"id": review_id}).first():
                raise HTTPException(status_code=404, detail="Review doesn't exist")
        
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username, games.game, review_name, optional_rating, optional_reviews.updated_at
                FROM reviews
                JOIN optional_reviews ON optional_reviews.review_id = reviews.id
                JOIN users ON users.id = reviews.user_id
                JOIN games ON games.id = reviews.game_id
                WHERE reviews.id = :review_id AND reviews.published = TRUE
                """
            ),
            {"review_id": review_id}
        )

    result = row.mappings().all()
    if not result:
        raise HTTPException(status_code=404, detail="Invalid Review ID") 
    
    return [GetOptionalReview(username=r["username"], game=r["game"],aspectToReview=r["review_name"],score=r["optional_rating"],updated_at=r["updated_at"]) for r in result]

@router.post("/{review_id}/comments", status_code=status.HTTP_200_OK, response_model=PostCommentResponse)
def post_comment(
    comment: CommentCreate
):
    start = time.time()
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": comment.review_id}).first():
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
                "review_id": comment.review_id,
                "user_id": comment.user_id,
                "text": comment.comment,
            }
        ).scalar_one()

        end = time.time()
        print(end - start)
        return PostCommentResponse(comment_id=result)

@router.get("/{review_id}/comments", status_code=status.HTTP_200_OK, response_model=List[Comment])
def get_comments(
    review_id: int, 
    limit: int = Query(10, description="Maximum number of comments to return")
):
    start = time.time()
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
    end = time.time()
    print(end - start)
    return comments