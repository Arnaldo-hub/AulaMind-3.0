"""Add user roles

Revision ID: 20260709_02
Revises: 20260708_01
"""

from alembic import op
import sqlalchemy as sa

revision = "20260709_02"
down_revision = "20260708_01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=30),
            nullable=False,
            server_default="teacher",
        ),
    )
    op.execute(
        """
        UPDATE users
        SET role = CASE
            WHEN is_admin = true THEN 'admin'
            ELSE 'teacher'
        END
        """
    )
    op.create_index("ix_users_role", "users", ["role"], unique=False)


def downgrade():
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
