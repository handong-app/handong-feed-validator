"""Regenerate table with Add id and Set id PK - TbKaMessage

Revision ID: 347339a2659e
Revises: 72682a02eea5
Create Date: 2024-09-15 20:00:35.354049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '347339a2659e'
down_revision: Union[str, None] = '72682a02eea5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TbKaMessage',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('client_message_id', sa.BigInteger(), nullable=False),
    sa.Column('room_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('distance', sa.Float(), nullable=False),
    sa.Column('threshold', sa.Float(), nullable=False),
    sa.Column('similar_id', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_sent_at', sa.Integer(), nullable=True),
    sa.Column('deleted', sa.String(length=1), nullable=True),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('TbSubject',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_sent_at', sa.Integer(), nullable=True),
    sa.Column('last_sent_chat_id', sa.BigInteger(), nullable=True),
    sa.Column('deleted', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('TbSubject')
    op.drop_table('TbKaMessage')
    # ### end Alembic commands ###
