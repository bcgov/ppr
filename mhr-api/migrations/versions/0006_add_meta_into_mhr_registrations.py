"""0006_add_meta_into_mhr_registrations

Revision ID: aed708d88460
Revises: 793f7c153047
Create Date: 2026-01-08 09:55:10.085326

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aed708d88460'
down_revision = '793f7c153047'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mhr_registrations', sa.Column('summary_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade():
    op.drop_column('mhr_registrations', 'summary_snapshot')
