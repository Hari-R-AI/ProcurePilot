"""Initial schema — ProcurePilot v0.2.0

Creates:
- procurement_requests (with status, budget_currency columns)
- recommendation_logs (with FK constraint to procurement_requests)

Revision ID: 0001
Revises: —
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "procurement_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("budget", sa.Float(), nullable=True),
        sa.Column("budget_currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column("urgency", sa.String(length=20), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("preferred_supplier", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="SUBMITTED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_procurement_requests_id"), "procurement_requests", ["id"])
    op.create_index(op.f("ix_procurement_requests_category"), "procurement_requests", ["category"])
    op.create_index(op.f("ix_procurement_requests_urgency"), "procurement_requests", ["urgency"])
    op.create_index(op.f("ix_procurement_requests_status"), "procurement_requests", ["status"])
    op.create_index(op.f("ix_procurement_requests_created_at"), "procurement_requests", ["created_at"])

    op.create_table(
        "recommendation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("procurement_request_id", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("normalized_request", sa.Text(), nullable=False),
        sa.Column("extracted_requirements", sa.Text(), nullable=False),
        sa.Column("policy_snippets", sa.Text(), nullable=False),
        sa.Column("risk_flags", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("recommendation_items", sa.Text(), nullable=False),
        sa.Column("recommendation_summary", sa.Text(), nullable=False),
        sa.Column("processing_time_ms", sa.Float(), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=False),
        sa.Column("trace_id", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["procurement_request_id"],
            ["procurement_requests.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recommendation_logs_id"), "recommendation_logs", ["id"])
    op.create_index(op.f("ix_recommendation_logs_procurement_request_id"), "recommendation_logs", ["procurement_request_id"])
    op.create_index(op.f("ix_recommendation_logs_confidence_score"), "recommendation_logs", ["confidence_score"])
    op.create_index(op.f("ix_recommendation_logs_request_id"), "recommendation_logs", ["request_id"])
    op.create_index(op.f("ix_recommendation_logs_trace_id"), "recommendation_logs", ["trace_id"])
    op.create_index(op.f("ix_recommendation_logs_created_at"), "recommendation_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("recommendation_logs")
    op.drop_table("procurement_requests")
