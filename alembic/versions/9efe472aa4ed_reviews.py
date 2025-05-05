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
        "Reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("published", sa.Boolean, default=False, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("game_id", sa.Integer, nullable=False),

    )

    op.create_table(
        "Users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, nullable=False),
        sa.Column("private_account", sa.Boolean, nullable=False),
    )

    op.create_table(
        "Friends",
        sa.Column("user_adding_id", sa.Integer, primary_key=True),
        sa.Column("user_added_id", sa.Integer, primary_key=True),
    )


    op.create_table(
        "Games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("genre_id", sa.Integer, nullable=False),
    )

    op.create_table(
        "Genres",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
    )
    op.create_table(
        "Optional_reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("review_name", sa.String, nullable=False),
        sa.Column("optional_rating", sa.Integer, nullable=False),
        sa.Column("review_id", sa.Integer, nullable=False)
    )

    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
