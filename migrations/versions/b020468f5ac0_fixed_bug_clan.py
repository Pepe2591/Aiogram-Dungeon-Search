"""Fixed bug clan

Revision ID: b020468f5ac0
Revises: ab79427136e4
Create Date: 2026-11-21 16:25:25.781367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b020468f5ac0'
down_revision: Union[str, Sequence[str], None] = 'ab79427136e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
