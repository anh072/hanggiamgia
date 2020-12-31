"""added vote count for posts

Revision ID: 3e9f466be54e
Revises: 36bf76f3cd9c
Create Date: 2020-12-31 21:47:57.434693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e9f466be54e'
down_revision = '36bf76f3cd9c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('votes', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'votes')
    # ### end Alembic commands ###
