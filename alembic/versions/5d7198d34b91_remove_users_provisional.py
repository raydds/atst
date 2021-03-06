"""remove users.provisional

Revision ID: 5d7198d34b91
Revises: 02ac8bdcf16f
Create Date: 2020-01-09 08:42:34.512191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d7198d34b91' # pragma: allowlist secret
down_revision = '02ac8bdcf16f' # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'provisional')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('provisional', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
