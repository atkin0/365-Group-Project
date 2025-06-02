from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

class PostDeletionResponse(BaseModel):
    success: bool


@router.delete("/delete", status_code=status.HTTP_200_OK, response_model=PostDeletionResponse)
def delete_post(review_id: int):
    with db.engine.begin() as connection:
        # First check if the review exists
        review_exists = connection.execute(
            sqlalchemy.text("SELECT 1 FROM reviews WHERE id = :review_id"),
            {"review_id": review_id}
        ).first() is not None
        
        if not review_exists:
            raise HTTPException(status_code=404, detail="Review not found")
            
        # Delete optional reviews first (foreign key relationship)
        optional_deleted = connection.execute(
            sqlalchemy.text("DELETE FROM optional_reviews WHERE review_id = :review_id"),
            {"review_id": review_id}
        ).rowcount
        
        # Then delete the main review
        review_deleted = connection.execute(
            sqlalchemy.text("DELETE FROM reviews WHERE id = :review_id"),
            {"review_id": review_id}
        ).rowcount
        
        return {
            "success": review_deleted > 0,
            "deleted_review": review_deleted > 0,
            "deleted_optional_reviews": optional_deleted
        }