"""Modify field name and type to last_sent_chat_id - TbSubject

Revision ID: 5cd4db0d1941
Revises: 6bd872082c90
Create Date: 2024-09-10 19:45:41.705837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5cd4db0d1941'
down_revision: Union[str, None] = '6bd872082c90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TbSubject', sa.Column('last_sent_chat_id', sa.BigInteger(), nullable=True))
    op.drop_column('TbSubject', 'last_sent_tb_ka_message_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TbSubject', sa.Column('last_sent_tb_ka_message_id', mysql.VARCHAR(length=32), nullable=True))
    op.drop_column('TbSubject', 'last_sent_chat_id')
    # ### end Alembic commands ###