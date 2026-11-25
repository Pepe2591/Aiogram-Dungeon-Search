"""Fixed bug

Revision ID: ab79427136e4
Revises: 3f91c4d9aac6
Create Date: 2026-11-21 16:24:00.916877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab79427136e4'
down_revision: Union[str, Sequence[str], None] = '3f91c4d9aac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
