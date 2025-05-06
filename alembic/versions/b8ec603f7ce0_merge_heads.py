"""merge heads

Revision ID: b8ec603f7ce0
Revises: 9efe472aa4ed, 0a997c26385c
Create Date: 2025-05-05 23:07:00.469742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8ec603f7ce0'
down_revision: Union[str, None] = ('9efe472aa4ed', '0a997c26385c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
