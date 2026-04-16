"""create prompts table

Revision ID: fe34dc765864
Revises: 4bd0dd009e46
Create Date: 2026-04-07 16:25:50.984213

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, VARCHAR, TIMESTAMP, BOOLEAN, text, func
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "fe34dc765864"
down_revision: Union[str, Sequence[str], None] = "4bd0dd009e46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prompts",
        Column("id", VARCHAR(256), primary_key=True),
        Column("project_id", VARCHAR(256), nullable=False),
        Column("base", JSONB(none_as_null=True)),
        Column("patches", JSONB),
        Column("text", VARCHAR(256), nullable=False),
        Column("status", VARCHAR(8)),
        Column(
            "dt_created",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        Column(
            "dt_done",
            TIMESTAMP(timezone=True),
            server_default=func.now(),
        ),
        Column("deleted", BOOLEAN, server_default=text("false")),
        schema="generator",
    )


def downgrade() -> None:
    op.drop_table("prompts", schema="generator")
