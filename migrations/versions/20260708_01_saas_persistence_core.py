"""AulaMind SaaS persistence core"""
from alembic import op
import sqlalchemy as sa

revision = "20260708_01"
down_revision = "20260708_00"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("school_id", sa.String(36), sa.ForeignKey("schools.id"), nullable=True),
        sa.Column("document_type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="generated"),
        sa.Column("course", sa.String(120)),
        sa.Column("subject", sa.String(200)),
        sa.Column("unit", sa.String(255)),
        sa.Column("topic", sa.String(255)),
        sa.Column("objectives_json", sa.JSON()),
        sa.Column("input_json", sa.JSON()),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index("ix_documents_document_type", "documents", ["document_type"])

    op.create_table("ai_generations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id")),
        sa.Column("feature", sa.String(50), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False, server_default="openai"),
        sa.Column("model", sa.String(100)),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_usd", sa.Numeric(12,6), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table("exports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("format", sa.String(20), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="requested"),
        sa.Column("file_path", sa.String(500)),
        sa.Column("file_size_bytes", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table("usage_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("school_id", sa.String(36), sa.ForeignKey("schools.id")),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("feature", sa.String(60), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

def downgrade():
    op.drop_table("usage_events")
    op.drop_table("exports")
    op.drop_table("ai_generations")
    op.drop_index("ix_documents_document_type", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")
