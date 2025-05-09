"""reviews

Revision ID: 9efe472aa4ed
Revises: 
Create Date: 2025-05-05 10:43:58.433269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9efe472aa4ed'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("published", sa.Boolean, server_default=sa.sql.expression.literal(False), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("game_id", sa.Integer, nullable=False),

    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, nullable=False),
        sa.Column("private_account", sa.Boolean, nullable=False),
    )

    op.create_table(
        "friends",
        sa.Column("user_adding_id", sa.Integer, primary_key=True),
        sa.Column("user_added_id", sa.Integer, primary_key=True),
    )


    op.create_table(
        "games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("genre_id", sa.Integer, nullable=False),
    )

    op.create_table(
        "genres",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
    )

    op.create_table(
        "optional_reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("review_name", sa.String, nullable=False),
        sa.Column("optional_rating", sa.Integer, nullable=False),
        sa.Column("review_id", sa.Integer, nullable=False)
    )

    op.create_table(
        "History",
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("game_id", sa.Integer, primary_key=True),
        sa.Column("time_played", sa.Float, primary_key=True),
    )

    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(
        "reviews"
    )

    op.drop_table(
        "users"
    )

    op.drop_table(
        "friends"
    )


    op.drop_table(
        "games"
    )

    op.drop_table(
        "genres"
    )
    op.drop_table(
        "optional_reviews"
    )
