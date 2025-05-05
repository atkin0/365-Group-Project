from fastapi import APIRouter, Depends
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/review",
    tags=["review"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/review/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def send_review():
    