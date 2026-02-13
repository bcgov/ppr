"""0007_add_drs_rejection_id_into_mhr_review_registrations

Revision ID: 639ae66d100b
Revises: aed708d88460
Create Date: 2026-02-11 14:40:10.515903

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '639ae66d100b'
down_revision = 'aed708d88460'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mhr_review_registrations', sa.Column('drs_rejection_id', sa.String(length=20), nullable=True),)


def downgrade():
    op.drop_column('mhr_review_registrations', 'drs_rejection_id')
