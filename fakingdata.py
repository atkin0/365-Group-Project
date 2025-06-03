import sqlalchemy
from faker import Faker
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



fake = Faker()
random = Random()
num_games = 500
num_users = 10000
num_reviews = 300000
num_optional_reviews = 2
num_comments = 2


with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""
    TRUNCATE reviews, users, friends, games, genres, optional_reviews, history, comments;
    """))

    print("genres")
    for genre in genres:
        conn.execute(sqlalchemy.text("""
        INSERT INTO genres (genre) VALUES (:genre);
        """), {"genre": genre})

    first_genre_id = conn.execute(
        sqlalchemy.text(
            """
            SELECT MIN(id) FROM genres
            """
        ),
    ).scalar_one()

    print("games")
    for _ in range(num_games):
        game_name = fake.company()
        game_genre = random.randint(first_genre_id, first_genre_id+10)
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

    first_game_id = conn.execute(
        sqlalchemy.text(
            """
            SELECT MIN(id) FROM games 
            """
        ),
    ).scalar_one()

    print("users")
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

    first_user_id = conn.execute(
        sqlalchemy.text(
            """
            SELECT MIN(id) FROM users 
            """
        ),
    ).scalar_one()

    print("history")
    for i in range(num_users):
        print(i) if i % 1000 == 0 else None
        for _ in range(random.randint(1, 5)):
            game_id = random.randint(first_game_id, first_game_id+num_games-1)
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
                {"user_id": i+first_user_id, "game_id": game_id, "time_played": time_played}
            )

    print("friends")
    for i in range(num_users):
        print(i) if i% 1000 == 0 else None
        for _ in range(random.randint(0,10)):
            random_friend_id = random.randint(first_user_id, first_user_id+num_users-1)
            while random_friend_id == i+first_user_id:
                random_friend_id = random.randint(first_user_id, first_user_id + num_users - 1)

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
                    "user_adding_id": i+first_user_id,
                    "user_added_id": random_friend_id,
                }
            )


for _ in range(100):
    print("reviews " + str(_))
    with engine.begin() as conn:
        for _ in range(num_reviews//100):
            user_id = random.randint(first_user_id, first_user_id+num_users-1)
            score = random.randint(1,10)
            text = fake.text(10)
            game_id = random.randint(first_game_id, first_game_id+num_games-1)

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
                optional_rating = random.randint(1,10)
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

            for _ in range(num_comments):
                user_id = random.randint(first_user_id, first_user_id + num_users - 1)
                text = fake.text(10)

                conn.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO comments (review_id, user_id, text) 
                        VALUES (:review_id, :user_id, :text);
                        """
                    ),
                    {
                        "review_id": review_id,
                        "user_id": user_id,
                        "text": text,
                    }
                )















