"""Soft delete for labels

Revision ID: 6b5fa54f6efc
Revises: eb893fd8080e
Create Date: 2024-11-14 16:25:07.006172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b5fa54f6efc'
down_revision = 'eb893fd8080e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('label_bundle', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('label_bundle', 'deleted')
    # ### end Alembic commands ###
