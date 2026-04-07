"""create generator schema

Revision ID: 4bd0dd009e46
Revises:
Create Date: 2026-04-07 16:24:24.978835

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4bd0dd009e46"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA generator")


def downgrade() -> None:
    op.execute("DROP SCHEMA generator")
