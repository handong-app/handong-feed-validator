"""empty message

Revision ID: 12002add81a6
Revises: 
Create Date: 2024-09-08 23:00:27.349892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '12002add81a6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TbKaMessage',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('message', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_sent_at', sa.DateTime(), nullable=True),
    sa.Column('subject_id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('mydb_TbKaFeed')
    op.drop_table('mydb_TbKaFeed_copy')
    op.drop_table('mydb_Tbfeed')
    op.drop_table('mydb_Tbuser')
    op.drop_table('exported_chat_logs_dec_db')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exported_chat_logs_dec_db',
    sa.Column('COL 1', mysql.VARCHAR(length=3), nullable=True),
    sa.Column('COL 2', mysql.VARCHAR(length=19), nullable=True),
    sa.Column('COL 3', mysql.VARCHAR(length=4), nullable=True),
    sa.Column('COL 4', mysql.VARCHAR(length=17), nullable=True),
    sa.Column('COL 5', mysql.VARCHAR(length=19), nullable=True),
    sa.Column('COL 6', mysql.VARCHAR(length=965), nullable=True),
    sa.Column('COL 7', mysql.VARCHAR(length=4691), nullable=True),
    sa.Column('COL 8', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('COL 9', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('COL 10', mysql.VARCHAR(length=18), nullable=True),
    sa.Column('COL 11', mysql.VARCHAR(length=19), nullable=True),
    sa.Column('COL 12', mysql.VARCHAR(length=7), nullable=True),
    sa.Column('COL 13', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('COL 14', mysql.VARCHAR(length=240), nullable=True),
    mysql_collate='utf8mb3_general_ci',
    mysql_default_charset='utf8mb3',
    mysql_engine='InnoDB'
    )
    op.create_table('mydb_Tbuser',
    sa.Column('id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('content', mysql.MEDIUMTEXT(), nullable=False),
    sa.Column('deleted', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('mpic', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('nick', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('phone', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('username', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('role', mysql.ENUM('ADMIN', 'USER'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('mydb_Tbfeed',
    sa.Column('id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('author', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('content', mysql.MEDIUMTEXT(), nullable=False),
    sa.Column('createdDate', mysql.DATETIME(fsp=6), nullable=True),
    sa.Column('deleted', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('modifiedDate', mysql.DATETIME(fsp=6), nullable=True),
    sa.Column('title', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('mydb_TbKaFeed_copy',
    sa.Column('id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('chatId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('clientMessageId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('createdDate', mysql.DATETIME(fsp=6), nullable=True),
    sa.Column('deleted', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('message', mysql.MEDIUMTEXT(), nullable=False),
    sa.Column('modifiedDate', mysql.DATETIME(fsp=6), nullable=True),
    sa.Column('roomId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('sentAt', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('userId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('mydb_TbKaFeed',
    sa.Column('id', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('chatId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('clientMessageId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('createdDate', mysql.DATETIME(fsp=6), nullable=True),
    sa.Column('deleted', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('message', mysql.MEDIUMTEXT(), nullable=False),
    sa.Column('modifiedDate', mysql.DATETIME(fsp=6), nullable=True),
    sa.Column('roomId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('sentAt', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('userId', mysql.BIGINT(display_width=20), autoincrement=False, nullable=False),
    sa.Column('duplicate_count', mysql.INTEGER(display_width=11), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.Column('original_message_id', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('TbKaMessage')
    # ### end Alembic commands ###
