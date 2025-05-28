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
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM reviews where id = :id"),
                {"id": review_id}).first():
            raise HTTPException(status_code=404, detail="review doesn't exist")

        result = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM optional_reviews
                WHERE review_id = :review_id;
                
                DELETE FROM reviews
                WHERE id = :review_id;
                """
            ),
            {"review_id": review_id},
        )

        if result.rowcount == 0:
            return PostDeletionResponse(success=False)
        else:
            return PostDeletionResponse(success=True)
