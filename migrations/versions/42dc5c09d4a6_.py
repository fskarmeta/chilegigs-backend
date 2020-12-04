"""empty message

Revision ID: 42dc5c09d4a6
Revises: 5a645d1fb996
Create Date: 2020-12-04 17:59:06.097619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42dc5c09d4a6'
down_revision = '5a645d1fb996'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('objetoglobales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('requisitos', sa.Text(), nullable=True),
    sa.Column('home', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('objetoglobales')
    # ### end Alembic commands ###
