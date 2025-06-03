import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np
from random import Random


# def database_connection_url():
#     dotenv.load_dotenv()
#     DB_USER: str = os.environ.get("POSTGRES_USER")
#     DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
#     DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
#     DB_PORT: str = os.environ.get("POSTGRES_PORT")
#     DB_NAME: str = os.environ.get("POSTGRES_DB")
#     return f"postgresql+psycopg://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


# Create a new DB engine based on our connection string

engine = sqlalchemy.create_engine("postgresql+psycopg://myuser:mypassword@localhost:5433/mydatabase", use_insertmanyvalues=True)
genres = ['FPS', 'Sandbox', 'Fighting', 'VR', 'Sports', 'Horror', 'Puzzle', 'RPG', 'Strategy',
              'Battle Royale', 'Adventure']

num_games = 500

fake = Faker()
random = Random()
num_users = 4
num_friends = 2
num_reviews = 40
num_optional_reviews = 1


with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    TRUNCATE reviews, users, friends, games, genres, optional_reviews, history, comments;
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

    for i in range(num_users):
        for _ in range(random.randint(1, 20)):
            game_id = random.randint(1, num_games)
            time_played = random.randint(1, 100)
            conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO history (user_id, game_id, time_played)
                    VALUES (:user_id, :game_id, :time_played)
                    ON CONFLICT (user_id, game_id) 
                    DO UPDATE SET
                    time_played = history.time_played + EXCLUDED.time_played;
                    """
                ),
                {"user_id": i, "game_id": game_id, "time_played": time_played}
            )

    for i in range(1, num_users+1):

        for _ in range(num_friends):
            random_friend_id = random.randint(1, num_users)
            conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO friends (user_adding_id, user_added_id) 
                    VALUES (:user_adding_id, :user_added_id)
                    ON CONFLICT (user_adding_id, user_added_id)
                    DO NOTHING
                    """
                ),
                {
                    "user_adding_id": i,
                    "user_added_id": random_friend_id,
                }
            )

    for _ in range(num_reviews):
        user_id = random.randint(1, num_users)
        score = int(np.random.normal() * 10)
        text = fake.text(10)
        game_id = random.randint(1, num_games)

        review_id = conn.execute(
            sqlalchemy.text(
                """
                INSERT INTO reviews (score, text, published, user_id, game_id) 
                VALUES (:score, :text, :published, :user_id, :game_id)
                RETURNING id
                """
            ),
            {
                "score": score,
                "text": text,
                "published": True,
                "user_id": user_id,
                "game_id": game_id
            }
        ).scalar_one()

        for i in range(num_optional_reviews):
            optional_rating = int(np.random.normal() * 10)
            review_name = fake.word()

            conn.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO optional_reviews (review_name, optional_rating, review_id) 
                    VALUES (:review_name, :optional_rating, :review_id);
                    """
                ),
                {
                    "review_name": review_name,
                    "optional_rating": optional_rating,
                    "review_id": review_id,
                }
            )















