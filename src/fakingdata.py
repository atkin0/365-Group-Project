import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np
from random import Random


def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql+psycopg://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)
genres = ['FPS', 'Sandbox', 'Fighting', 'VR', 'Sports', 'Horror', 'Puzzle', 'RPG', 'Strategy',
              'Battle Royale', 'Adventure']

num_games = 500

fake = Faker()
random = Random()
num_users = 20000
num_friends = 20
num_reviews = 400000


with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    TRUNCATE reviews;
    TRUNCATE users;
    TRUNCATE friends;
    TRUNCATE games;
    TRUNCATE genres;
    TRUNCATE optional_reviews;
    TRUNCATE history;
    TRUNCATE comments;
    """))

    for genre in genres:
        conn.execute(sqlalchemy.text("""
        INSERT INTO genres (genre) VALUES (:genre);
        """), {"genre": genre})

    for _ in range(num_games):
        game_name = fake.company()
        game_genre = random.randint(1, 11)
        conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO games (game, genre_id) 
                VALUES (:game_name, :game_genre);
                """
             ),
             {
                 "game_name": game_name,
                 "game_genre": game_genre
             }
        )

    for _ in range(num_users):
        username = fake.name()
        conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username) 
                VALUES (:username);
                """
            ),
            {
                "username": username,
            }
        )



    for i in range(1, num_users+1):

        for i in range(num_friends):
            random_friend_id = random.randint(1, num_users)
            conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO friends (user_adding_id, user_added_id) 
                    VALUES (:user_adding_id, user_added_id);
                    """
                ),
                {
                    "user_adding_id": i,
                    "user_added_id": random_friend_id,
                }
            )

    for _ in range(num_reviews):
        random_user_id = random.randint(1, num_users)
        score = int(np.random.normal() * 10)
        text = fake.text(10)













