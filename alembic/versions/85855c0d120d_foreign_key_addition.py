"""foreign key addition

Revision ID: 85855c0d120d
Revises: e263797d0b5c
Create Date: 2025-06-02 17:11:37.513615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85855c0d120d'
down_revision: Union[str, None] = 'e263797d0b5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("optional_reviews")
    op.drop_table("reviews")
    op.drop_table("games")
    
    op.create_table(
        "games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("game", sa.String, nullable=False),
        sa.Column("genre_id", sa.Integer,  sa.ForeignKey("genres.id") , nullable=False)
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("published", sa.Boolean, server_default=sa.sql.expression.literal(False), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("game_id", sa.Integer, sa.ForeignKey("games.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    op.create_table(
        "optional_reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("review_name", sa.String, nullable=False),
        sa.Column("optional_rating", sa.Integer, nullable=False),
        sa.Column("review_id", sa.Integer, sa.ForeignKey("reviews.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("review_name", "review_id", name="uq_review_name_review_id")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("optional_reviews")
    op.drop_table("reviews")
    op.drop_table("games")

    op.create_table(
        "optional_reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("review_name", sa.String, nullable=False),
        sa.Column("optional_rating", sa.Integer, nullable=False),
        sa.Column("review_id", sa.Integer, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("published", sa.Boolean, server_default=sa.sql.expression.literal(False), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("game_id", sa.Integer, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )

    op.create_table(
        "games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("game", sa.String, nullable=False),
        sa.Column("genre_id", sa.Integer, nullable=False)
    )
