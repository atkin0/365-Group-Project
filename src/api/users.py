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

class User(BaseModel):
    user_id: int
    username: str

class Setting(BaseModel):
    setting_id: int
    private: int

class Edit_Setting(BaseModel):
    id: int
    name: str
    value: int

class Reviews(BaseModel):
    user_id: int
    game_id: int
    score: int
    description: str



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
                INSERT INTO users (user_id, private)
                VALUES (:user_id, :private)
                RETURNING id
                """
            ),
            [{"user_id": result, "private": new_user.private}],
        )

    return UserCreateResponse(cart_id=result)

@router.get("/{user_id}/add",  status_code=status.HTTP_204_NO_CONTENT)
def add_friends(user: User, friend: User):
    """
    Add a user as a friend.
    """
    with db.engine.begin() as connection:
        friends = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (user_adding_id, user_added_id)
                VALUES (:user_adding_id, :user_added_id)
                """
            ),
            [{"user_adding_id": user.user_id, "user_added_id": user.user_id}]
        )
        
    pass


@router.get("/{user_id}/friends", response_model= list[User])
def display_friends(new_user: User):
    """
    Display a users list of friends.
    """
    friends_list = []
    with db.engine.begin() as connection:
        friends = connection.execute(
            sqlalchemy.text(
                """
                SELECT f1.user_added_id AS id
                FROM friends as f1
                JOIN friends as f2 ON f1.user_adding_id = f2.user_added_id AND f1.user_added_id = f2.user_adding_id
                WHERE f1.user_adding_id = :user_id;
                """
            ),
        )
        for friend in friends:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id, username
                    FROM users
                    WHERE id = :friend_id
                    """
                ),
                [{"friend_id": friend.id}],
            )
            friends_list.append(User(user_id=result.id, user_name= result.username))
        
    return friends_list

@router.get("/{user_id}/settings", response_model= Setting)
def show_settings(user: User):
    """
    Display a users settings.
    """
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM settings
                where user_id = :user_id
                """
            ),
            [{"user_id": user.user_id}]
        )
        
    return Setting(setting_id = result.id, private= result.private)

@router.patch("/{user_id}/settings/edit", status_code=status.HTTP_204_NO_CONTENT)
def edit_settings(setting: Edit_Setting):
    """
    Edit a users settings.
    """
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                UPDATE settings
                SET :setting_name = :setting_value
                WHERE setting_id = :setting_id
                """
            ),
            [{"setting_name": setting.name, "setting_value": setting.value, "setting_id": setting.id}]
        )
        
    pass 

@router.get("/{user_id}/history", response_model= list[Reviews])
def show_history(user: User):
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
            [{"user_id": user.user_id}]
        )
        for review in result:
            reviews_list.append(
                Reviews(
                    user_id= user.user_id, 
                    game_id=result.game_id, 
                    score = result.score, 
                    description=result.description
                )
            )
        
    return reviews_list


@router.get("/{user_id}/favorite", response_model= list[Reviews])
def show_top(user: User):
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
            [{"user_id": user.user_id}]
        )
        for review in result:
            reviews_list.append(
                Reviews(
                    user_id= user.user_id, 
                    game_id=result.game_id, 
                    score = result.score, 
                    description=result.description
                )
            )
        
    return reviews_list
