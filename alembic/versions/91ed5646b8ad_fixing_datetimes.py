"""fixing datetimes

Revision ID: 91ed5646b8ad
Revises: 9efe472aa4ed
Create Date: 2025-05-16 22:42:24.410992

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91ed5646b8ad'
down_revision: Union[str, None] = '9efe472aa4ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.drop_column('reviews', 'updated_at')
    op.drop_column('optional_reviews', 'updated_at')
    op.drop_column('history', 'last_played')
    op.drop_column('comments', 'updated_at')

    op.add_column('reviews',
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        )
    )

    op.add_column('optional_reviews',
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        )
    )

    op.add_column('history',
        sa.Column(
            "last_played",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        )
    )

    op.add_column('comments',
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False
        )
    )

def downgrade() -> None:
    op.drop_column('reviews', 'updated_at')
    op.drop_column('optional_reviews', 'updated_at')
    op.drop_column('history', 'last_played')
    op.drop_column('comments', 'updated_at')

    op.add_column('reviews', sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False))
    op.add_column('optional_reviews', sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False))
    op.add_column('history', sa.Column("last_played", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False))
    op.add_column('comments', sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False))

