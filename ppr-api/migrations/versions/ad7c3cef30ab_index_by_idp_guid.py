"""index-by-idp-guid

Revision ID: ad7c3cef30ab
Revises: 1ef89b6dbbcd
Create Date: 2022-12-13 10:04:42.587716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad7c3cef30ab'
down_revision = '1ef89b6dbbcd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_user_idp_userid'), 'users', ['idp_userid'], unique=True)
    op.create_unique_constraint('users_idp_userid_key', 'users', ['idp_userid'])


def downgrade():
    op.drop_index(op.f('ix_user_idp_userid'), table_name='users')
    op.drop_constraint('users_idp_userid_key', 'users', ['idp_userid'])
