"""Add Indian compliance fields

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add vendor compliance fields to procurement_requests
    op.add_column("procurement_requests", sa.Column("vendor_gstin", sa.String(length=15), nullable=True))
    op.add_column("procurement_requests", sa.Column("vendor_pan", sa.String(length=10), nullable=True))
    op.add_column("procurement_requests", sa.Column("msme_registered", sa.Boolean(), nullable=False, server_default=sa.text("0")))
    op.add_column("procurement_requests", sa.Column("udyam_number", sa.String(length=20), nullable=True))

    # Add compliance status to recommendation_logs
    op.add_column("recommendation_logs", sa.Column("compliance_status", sa.String(length=20), nullable=False, server_default="PENDING_REVIEW"))
    op.add_column("recommendation_logs", sa.Column("compliance_reasoning", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("recommendation_logs", "compliance_reasoning")
    op.drop_column("recommendation_logs", "compliance_status")

    op.drop_column("procurement_requests", "udyam_number")
    op.drop_column("procurement_requests", "msme_registered")
    op.drop_column("procurement_requests", "vendor_pan")
    op.drop_column("procurement_requests", "vendor_gstin")
