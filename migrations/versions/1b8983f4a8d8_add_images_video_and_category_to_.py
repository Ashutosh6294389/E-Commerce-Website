"""Add images, video, and category to Product model

Revision ID: 1b8983f4a8d8
Revises: b4a75fb0d822
Create Date: 2025-05-15 03:01:12.202950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b8983f4a8d8'
down_revision = 'b4a75fb0d822'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('images', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('video', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('category')
        batch_op.drop_column('video')
        batch_op.drop_column('images')

    # ### end Alembic commands ###
