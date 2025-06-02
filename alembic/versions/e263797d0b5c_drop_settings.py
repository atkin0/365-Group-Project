"""Drop settings

Revision ID: e263797d0b5c
Revises: 9e15e4c543e7
Create Date: 2025-06-01 14:32:18.532764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e263797d0b5c'
down_revision: Union[str, None] = '9e15e4c543e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("settings")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, nullable=False),
        sa.Column("account_is_private", sa.Boolean(), nullable=False, server_default=sa.text("true"))
    )
