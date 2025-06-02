"""Fix settings

Revision ID: 9e15e4c543e7
Revises: bfff6148d0b3
Create Date: 2025-06-01 01:56:31.167083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e15e4c543e7'
down_revision: Union[str, None] = 'bfff6148d0b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, nullable=False),
        sa.Column("account_is_private", sa.Boolean(), nullable=False, server_default=sa.text("true"))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("settings")
