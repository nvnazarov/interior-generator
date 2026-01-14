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
        Column("id", UUID(), primary_key=True, server_default=text("gen_random_uuid()")),
        Column("account_id", UUID(), nullable=False),
        Column("name", VARCHAR(256), nullable=False, server_default=""),
        Column("description", VARCHAR(2048), nullable=False, server_default=""),
        Column("pinned", BOOLEAN, nullable=False, server_default=text("false")),
        Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("deleted", BOOLEAN, nullable=False, server_default=text("false")),
        schema="projects",
    )
    op.create_table(
        "shells",
        Column("id", UUID(), primary_key=True, server_default=text("gen_random_uuid()")),
        Column("account_id", UUID(), nullable=False),
        Column("name", VARCHAR(256), nullable=False, server_default=""),
        Column("content", JSONB, nullable=False),
        Column("version", INTEGER, nullable=False, server_default="0"),
        Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("deleted", BOOLEAN, nullable=False, server_default=text("false")),
        schema="projects",
    )
    op.create_table(
        "plans",
        Column("id", UUID(), primary_key=True, server_default=text("gen_random_uuid()")),
        Column("project_id", UUID(), ForeignKey("projects.projects.id", ondelete="CASCADE"), nullable=False),
        Column("shell_id", UUID(), ForeignKey("projects.shells.id", ondelete="CASCADE"), nullable=False),
        Column("name", VARCHAR(256), nullable=False, server_default=""),
        Column("content", JSONB(), nullable=False),
        Column("version", INTEGER, nullable=False, server_default="0"),
        Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
        Column("deleted", BOOLEAN, nullable=False, server_default=text("false")),
        schema="projects",
    )
    op.create_table(
        "plans_per_project_quota",
        Column("project_id", UUID(), ForeignKey("projects.projects.id", ondelete="CASCADE"), primary_key=True),
        Column("current_plans_count", INTEGER, server_default="0"),
        Column("max_plans_count", INTEGER, nullable=False),
        Column("version", INTEGER, nullable=False, server_default="0"),
        schema="projects",
    )
    op.create_table(
        "projects_quota",
        Column("account_id", UUID(), primary_key=True),
        Column("current_projects_count", INTEGER, server_default="0"),
        Column("max_projects_count", INTEGER, nullable=False),
        Column("version", INTEGER, nullable=False, server_default="0"),
        schema="projects",
    )
    op.create_table(
        "shells_quota",
        Column("account_id", UUID(), primary_key=True),
        Column("current_shells_count", INTEGER, server_default="0"),
        Column("max_shells_count", INTEGER, nullable=False),
        Column("version", INTEGER, nullable=False, server_default="0"),
        schema="projects",
    )
    op.create_index("idx_projects_account_id", "projects", ["account_id"], schema="projects")
    op.create_index("idx_shells_account_id", "shells", ["account_id"], schema="projects")
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
    op.execute("DROP TRIGGER sync_project_update_time_trigger ON plans")
    op.execute("DROP FUNCTION sync_project_update_time() CASCADE")
    op.drop_index("idx_plans_project_id", "plans")
    op.drop_index("idx_shells_account_id", "shells")
    op.drop_index("idx_projects_account_id", "projects")
    op.drop_table("shells_quota")
    op.drop_table("projects_quota")
    op.drop_table("plans_per_project_quota")
    op.drop_table("plans")
    op.drop_table("shells")
    op.drop_table("projects")
    op.execute("DROP SCHEMA projects")
