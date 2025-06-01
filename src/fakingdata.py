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
num_users = 200000

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

    # populate initial posting categories
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








posts_sample_distribution = np.random.default_rng().negative_binomial(0.04, 0.01, num_users)
category_sample_distribution = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                                num_users,
                                                p=[0.1, 0.05, 0.1, 0.3, 0.05, 0.05, 0.05, 0.05, 0.15, 0.1])
total_posts = 0

# create fake posters with fake names and birthdays
with engine.begin() as conn:
    print("creating fake posters...")
    posts = []
    for i in range(num_users):
        if (i % 10 == 0):
            print(i)

        profile = fake.profile()
        username = fake.unique.email()
        device_type = fake.random_element(elements=('Android', 'iOS', 'Web'))

        poster_id = conn.execute(sqlalchemy.text("""
        INSERT INTO users (username, full_name, birthday, device_type) VALUES (:username, :name, :birthday, :device_type) RETURNING id;
        """), {"username": username, "name": profile['name'], "birthday": profile['birthdate'],
               "device_type": device_type}).scalar_one();

        num_posts = posts_sample_distribution[i]
        likes_sample_distribution = np.random.default_rng().negative_binomial(0.8, 0.0001, num_posts)
        for j in range(num_posts):
            total_posts += 1
            posts.append({
                "title": fake.sentence(),
                "content": fake.text(),
                "poster_id": poster_id,
                "category_id": category_sample_distribution[i].item(),
                "visible": fake.boolean(75),
                "created_at": fake.date_time_between(start_date='-5y', end_date='now', tzinfo=None),
                "likes": likes_sample_distribution[j].item(),
                "nsfw": fake.boolean(10)
            })

    if posts:
        conn.execute(sqlalchemy.text("""
        INSERT INTO posts (title, content, poster_id, category_id, visible, created_at) 
        VALUES (:title, :content, :poster_id, :category_id, :visible, :created_at);
        """), posts)

    print("total posts: ", total_posts)
