from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Query
from pydantic import BaseModel, Field, constr
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)

class UserCreateResponse(BaseModel):
    user_id: int

class CreateUser(BaseModel):
    username: constr(min_length=3, max_length=50) = Field(..., description="Username must be between 3 and 50 characters")
    private: bool 

class Setting(BaseModel):
    name: str
    privacy_value: bool

class Reviews(BaseModel):
    user_id: int
    game_id: int
    score: int
    text: str



@router.post("/create", response_model=UserCreateResponse)
def create_user(new_user: CreateUser):
    """
    Creates a new User
    """

    print(f"NEW USER: {new_user}")
    with db.engine.begin() as connection:

        #Inserts new user info into the username table
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username, account_is_private)
                VALUES (:username, :privacy)
                RETURNING id
                """
            ),
            {"username": new_user.username, "privacy": new_user.private},
        ).scalar_one()
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO settings (user_id, name, value)
                VALUES (:user_id, 'private', :private_value)
                """
            ),
            {"user_id": result, "username": new_user.username, "private_value": new_user.private},
        )

    return UserCreateResponse(user_id=result)

@router.post("/{user_id}/add",  status_code=status.HTTP_204_NO_CONTENT)
def add_friends(user_id: int, friend_id: int):
    """
    Add a user as a friend.
    """
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": friend_id}).first():
            raise HTTPException(status_code=404, detail="Friend doesn't exist")

        friends = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO friends (user_adding_id, user_added_id)
                VALUES (:user_adding_id, :user_added_id)
                """
            ),
            {"user_adding_id": user_id, "user_added_id": friend_id}
        )
        


@router.get("/{user_id}/my_friends", response_model= List[str])
def display_my_friended(user_id: int):
    """
    Display a users list of friends.
    """
    friends_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username
                FROM friends
                JOIN users on friends.user_added_id = users.id
                WHERE friends.user_adding_id = :user_id;
                """
            ),
            {"user_id": user_id}
        )

        for r in results:
            friends_list.append(r.username)

    return friends_list

@router.get("/{user_id}/friended_me", response_model= List[str])
def display_friended_me(user_id: int):
    """
    Display a users list of friends.
    """

    friends_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username
                FROM friends
                JOIN users on friends.user_adding_id = users.id
                WHERE friends.user_added_id = :user_id;
                """
            ),
            {"user_id": user_id}
        )

        for r in results:
            friends_list.append(r.username)

    return friends_list

@router.get("/{user_id}/settings", response_model= list[Setting])
def show_settings(user_id: int):
    """
    Display a users settings.
    """
    setting_list = []
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT username, account_is_private
                FROM users
                WHERE id = :id
                """
            ),
            {"id": user_id}
        ).fetchall()
        
        for row in results:
            setting_list.append(
                Setting(
                    name=row.username,
                    privacy_value=row.account_is_private
                )
            )
        
    return setting_list

@router.patch("/{user_id}/settings/edit", status_code=status.HTTP_204_NO_CONTENT)
def edit_settings(user_id: int, setting: Setting):
    """
    Edit a users settings.
    """ 

    #setting.value should be passed in as true or false

    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")
        connection.execute(
            sqlalchemy.text(
                    """
                    UPDATE users
                    SET account_is_private = :privacy_value, username = :username
                    WHERE id = :id
                    """
            ),
            {"privacy_value": setting.privacy_value, "username": setting.name, "id": user_id}
        )
        
@router.get("/{user_id}/history", response_model=list[Reviews])
def show_history(
    user_id: int, 
    limit: int = Query(10, description="Maximum number of history items to return")
):
    """
    Display a users history.
    """
    reviews_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM reviews
                WHERE user_id = :user_id
                ORDER BY updated_at DESC
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "limit": limit}
        )
        for review in result:
            reviews_list.append(
                Reviews(
                    user_id= user_id,
                    game_id=review.game_id, 
                    score = review.score, 
                    text=review.text
                )
            )
        
    return reviews_list


@router.get("/{user_id}/favorite", response_model= list[Reviews])
def show_top(user_id: int):
    """
    Display a users history.
    """
    reviews_list = []
    with db.engine.begin() as connection:
        if not connection.execute(
                sqlalchemy.text("SELECT 1 FROM users where id = :id"),
                {"id": user_id}).first():
            raise HTTPException(status_code=404, detail="User doesn't exist")

        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM reviews
                WHERE user_id = :user_id
                ORDER BY score DESC
                LIMIT 5
                """
            ),
            {"user_id": user_id}
        ).fetchall()

    for review in result:
        reviews_list.append(
            Reviews(
                user_id= user_id,
                game_id=review.game_id,
                score = review.score,
                text=review.text
            )
        )
    return reviews_list
