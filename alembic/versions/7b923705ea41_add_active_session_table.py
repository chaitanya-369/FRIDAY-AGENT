"""add_active_session_table

Revision ID: 7b923705ea41
Revises:
Create Date: 2026-04-23 02:30:51.437813

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b923705ea41"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the active_session singleton table."""
    op.create_table(
        "active_session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_name", sa.String(), nullable=False),
        sa.Column("model_id", sa.String(), nullable=False),
        sa.Column("set_by", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("switched_at", sa.DateTime(), nullable=False),
        sa.Column("switch_history", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop the active_session table."""
    op.drop_table("active_session")
