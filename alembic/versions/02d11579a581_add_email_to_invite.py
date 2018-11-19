"""Add email to invite

Revision ID: 02d11579a581
Revises: 4c0b8263d800
Create Date: 2018-11-19 14:51:33.178358

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '02d11579a581'
down_revision = '4c0b8263d800'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('invitations', sa.Column('email', sa.String()))
    conn = op.get_bind()
    # Add non-null value to email column
    conn.execute(
        text(
            """
                insert into invitations (email)
                select u.email
                from invitations i
                inner join workspace_roles wr on i.workspace_role_id = wr.id
                inner join users u on wr.user_id = u.id
                where i.email is null;
            """
        )
    )
    conn.execute(
        text(
            """
                update invitations
                set email = 'example@example.com'
                where email is null;
            """
        )
    )
    op.alter_column('invitations', 'email', nullable=False)

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('invitations', 'email')
    # ### end Alembic commands ###
