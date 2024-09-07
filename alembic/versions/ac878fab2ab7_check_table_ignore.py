"""Check Table ignore

Revision ID: ac878fab2ab7
Revises: 6793d20f0dd9
Create Date: 2024-09-09 00:24:38.625273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'ac878fab2ab7'
down_revision: Union[str, None] = '6793d20f0dd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mydb_TbKaFeed_copy')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mydb_TbKaFeed_copy',
    sa.Column('id', mysql.VARCHAR(length=32), nullable=False),
    sa.Column('message', mysql.VARCHAR(length=500), nullable=False),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('last_sent_at', mysql.DATETIME(), nullable=True),
    sa.Column('subject_id', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
