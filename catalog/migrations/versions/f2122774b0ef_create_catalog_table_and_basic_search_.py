"""create catalog table and basic search indices

Revision ID: f2122774b0ef
Revises:
Create Date: 2026-01-17 21:55:55.904020

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, JSONB, VARCHAR

# revision identifiers, used by Alembic.
revision: str = "f2122774b0ef"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE SCHEMA catalog")
    op.create_table(
        "catalog",
        Column("id", VARCHAR(256), primary_key=True),
        Column("name", VARCHAR(256), nullable=False),
        Column("width", INTEGER, nullable=False),
        Column("height", INTEGER, nullable=False),
        Column("depth", INTEGER, nullable=False),
        Column("model_path", VARCHAR(512), nullable=False),
        Column("icon_path", VARCHAR(512), nullable=False),
        Column("thumbnail_path", VARCHAR(512), nullable=False),
        Column("mount", VARCHAR(16), nullable=False),
        Column("meta", JSONB),
        schema="catalog",
    )
    op.execute(
        "CREATE INDEX idx_catalog_name_trgm ON catalog.catalog USING gin (name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX idx_catalog_meta_area ON catalog.catalog((meta ->> 'area'))"
    )


def downgrade() -> None:
    op.drop_index("idx_catalog_meta_area", "catalog", schema="catalog")
    op.drop_index("idx_catalog_name_trgm", "catalog", schema="catalog")
    op.drop_table("catalog", schema="catalog")
    op.execute("DROP SCHEMA catalog")
