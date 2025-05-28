from typing import List

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
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
    username: str
    private: int

class Setting(BaseModel):
    id: int
    name: str
    value: int

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
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username)
                VALUES (:username)
                RETURNING id
                """
            ),
            [{"username": new_user.username}],
        ).scalar_one()
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO settings (user_id, name, value)
                VALUES (:user_id, 'private', :private_value)
                """
            ),
            [{"user_id": result, "private_value": new_user.private}],
        )

    return UserCreateResponse(user_id=result)

@router.post("/{user_id}/add",  status_code=status.HTTP_204_NO_CONTENT)
def add_friends(user_id: int, friend_id: int):
    """
    Add a user as a friend.
    """
    with db.engine.begin() as connection:
        friends = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO friends (user_adding_id, user_added_id)
                VALUES (:user_adding_id, :user_added_id)
                """
            ),
            [{"user_adding_id": user_id, "user_added_id": friend_id}]
        )
        


@router.get("/{user_id}/friends", response_model= List[str])
def display_my_friended(user_id: int):
    """
    Display a users list of friends.
    """
    friends_list = []
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username
                FROM friends
                JOIN users on friends.user_added_id = users.id
                WHERE friends.user_adding_id = :user_id;
                """
            ),
            [{"user_id": user_id}]
        )

        for r in results:
            friends_list.append(r.username)

    return friends_list

@router.get("/{user_id}/friends", response_model= List[str])
def display_friended_me(user_id: int):
    """
    Display a users list of friends.
    """
    friends_list = []
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT users.username
                FROM friends
                JOIN users on friends.user_adding_id = users.id
                WHERE friends.user_added_id = :user_id;
                """
            ),
            [{"user_id": user_id}]
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
                SELECT id, name, value
                FROM settings
                WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}]
        ).fetchall()
        
        for row in results:
            setting_list.append(
                Setting(
                    id=row.id,
                    name=row.name,
                    value=row.value
                )
            )
        
    return setting_list

@router.patch("/{user_id}/settings/edit", status_code=status.HTTP_204_NO_CONTENT)
def edit_settings(user_id: int, setting: Setting):
    """
    Edit a users settings.
    """
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE settings
                SET value = :value
                WHERE id = :id AND user_id = :user_id AND name = :name
                """
            ),
            [{"value": setting.value, "id": setting.id, "user_id": user_id, "name" :setting.name}]
        )
        
@router.get("/{user_id}/history", response_model= list[Reviews])
def show_history(user_id: int):
    """
    Display a users history.
    """
    reviews_list = []
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM reviews
                WHERE user_id = :user_id
                """
            ),
            [{"user_id": user_id}]
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
            [{"user_id": user_id}]
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
