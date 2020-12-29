"""Initial migration

Revision ID: f3005bd87c37
Revises: 
Create Date: 2020-12-28 18:39:11.276300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3005bd87c37'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('url', sa.String(length=200), nullable=True),
    sa.Column('coupon_code', sa.String(length=20), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_created_time'), 'posts', ['created_time'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author', sa.String(length=80), nullable=False),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_created_time'), 'comments', ['created_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comments_created_time'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_posts_created_time'), table_name='posts')
    op.drop_table('posts')
    op.drop_table('categories')
    # ### end Alembic commands ###