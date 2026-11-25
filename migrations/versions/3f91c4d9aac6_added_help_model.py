"""Added help model

Revision ID: 3f91c4d9aac6
Revises: a9b72813ecdf
Create Date: 2026-11-21 16:19:14.371733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f91c4d9aac6'
down_revision: Union[str, Sequence[str], None] = 'a9b72813ecdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
