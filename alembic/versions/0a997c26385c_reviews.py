"""reviews

Revision ID: 9efe472aa4ed
Revises: 
Create Date: 2025-05-05 10:43:58.433269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a997c26385c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
