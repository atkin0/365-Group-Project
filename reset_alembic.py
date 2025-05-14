from sqlalchemy import create_engine, text

# Your DB URL (note: use 'postgresql' not 'postgresql+psycopg' here)
engine = create_engine("postgresql://myuser:mypassword@localhost/mydatabase")

with engine.connect() as conn:
    conn.execute(text("DELETE FROM alembic_version"))
    conn.commit()

print("✔ alembic_version table cleared")
