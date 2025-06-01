"""more game information

Revision ID: 5ca46c8c42dc
Revises: 91ed5646b8ad
Create Date: 2025-05-31 14:45:01.052782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

from src.api.review import optional_review

# revision identifiers, used by Alembic.
revision: str = '5ca46c8c42dc'
down_revision: Union[str, None] = '91ed5646b8ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column("games", sa.Column("platforms", psql.ARRAY(sa.String()), nullable=True))
    op.add_column("games", sa.Column("multiplayer", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("games", "platforms")
    op.drop_column("games", "multiplayer")
