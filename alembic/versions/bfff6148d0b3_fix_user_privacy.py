"""Fix user privacy

Revision ID: bfff6148d0b3
Revises: 91ed5646b8ad
Create Date: 2025-06-01 01:41:33.871472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfff6148d0b3'
down_revision: Union[str, None] = '5ca46c8c42dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("users","private_account")

    #default to True to protect user settings
    op.add_column("users",sa.Column("account_is_private", sa.Boolean(),nullable=False,server_default=sa.text("true")))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users","account_is_private")
