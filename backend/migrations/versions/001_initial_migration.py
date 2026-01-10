"""Initial migration - create league and match tables

Revision ID: 001_initial
Revises:
Create Date: 2026-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "league",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "match",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("block_name", sa.String(), nullable=True),
        sa.Column("number_of_matches", sa.Integer(), nullable=False),
        sa.Column("team_a", sa.String(), nullable=True),
        sa.Column("team_b", sa.String(), nullable=True),
        sa.Column("league_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["league_id"],
            ["league.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("match")
    op.drop_table("league")
