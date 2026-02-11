"""create projects, shells and plans tables

Revision ID: c106552b639a
Revises:
Create Date: 2026-01-07 13:27:40.768410

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import (
    BOOLEAN,
    INTEGER,
    JSONB,
    TIMESTAMP,
    UUID,
    VARCHAR,
)
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = "c106552b639a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # fmt: off
    op.execute("CREATE SCHEMA projects")
    op.create_table(
        "projects",
        Column("id", UUID(), primary_key=True),
        Column("account_id", UUID(), nullable=False),
        Column("name", VARCHAR(256), nullable=False),
        Column("description", VARCHAR(2048), nullable=False),
        Column("revision", INTEGER, nullable=False),
        Column("content", JSONB(), nullable=False),
        Column("plans_count", INTEGER, nullable=False),
        Column("plans_limit", INTEGER, nullable=False),
        Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("published", BOOLEAN, nullable=False, server_default=text("false")),
        Column("deleted", BOOLEAN, nullable=False, server_default=text("false")),
        Column("version", INTEGER, nullable=False),
        schema="projects",
    )
    op.create_table(
        "plans",
        Column("id", UUID(), primary_key=True),
        Column("project_id", UUID(), ForeignKey("projects.projects.id", ondelete="CASCADE"), nullable=False),
        Column("name", VARCHAR(256), nullable=False),
        Column("revision", INTEGER, nullable=False),
        Column("content", JSONB(), nullable=False),
        Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("deleted", BOOLEAN, nullable=False, server_default=text("false")),
        Column("version", INTEGER, nullable=False),
        schema="projects",
    )
    op.create_table(
        "accounts",
        Column("account_id", UUID(), primary_key=True),
        Column("projects_count", INTEGER, nullable=False),
        Column("projects_limit", INTEGER, nullable=False),
        Column("version", INTEGER, nullable=False),
        schema="projects",
    )
    op.create_index("idx_projects_account_id", "projects", ["account_id"], schema="projects")
    op.create_index("idx_plans_project_id", "plans", ["project_id"], schema="projects")
    op.execute(
        "CREATE OR REPLACE FUNCTION sync_project_update_time() "
        "RETURNS TRIGGER AS $$ "
        "BEGIN "
        "    UPDATE projects.projects "
        "    SET updated_at = now() "
        "    WHERE id = NEW.project_id; "
        "    RETURN NEW; "
        "END; "
        "$$ LANGUAGE plpgsql"
    )
    op.execute(
        "CREATE OR REPLACE TRIGGER sync_project_update_time_trigger "
        "AFTER UPDATE ON projects.plans "
        "FOR EACH ROW "
        "EXECUTE FUNCTION sync_project_update_time()"
    )
    # fmt: on


def downgrade() -> None:
    op.execute("DROP TRIGGER sync_project_update_time_trigger ON projects.plans")
    op.execute("DROP FUNCTION sync_project_update_time() CASCADE")
    op.drop_index("idx_plans_project_id", "plans", schema="projects")
    op.drop_index("idx_projects_account_id", "projects", schema="projects")
    op.drop_table("accounts", schema="projects")
    op.drop_table("plans", schema="projects")
    op.drop_table("projects", schema="projects")
    op.execute("DROP SCHEMA projects")
