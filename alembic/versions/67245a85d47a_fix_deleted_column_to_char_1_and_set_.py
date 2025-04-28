"""fix deleted column to CHAR(1) and set default for is_tag_assigned and fix TbKaMessage.similar_id and TbKaMessage.id column to CHAR(32)

Revision ID: 67245a85d47a
Revises: e5492ed75525
Create Date: 2025-04-28 21:18:10.677140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '67245a85d47a'
down_revision: Union[str, None] = 'e5492ed75525'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('TbKaMessage', 'id',
               existing_type=mysql.VARCHAR(length=32),
               type_=sa.CHAR(length=32),
               existing_nullable=False)
    op.alter_column('TbKaMessage', 'similar_id',
               existing_type=mysql.VARCHAR(length=32),
               type_=sa.CHAR(length=32),
               existing_nullable=False)
    op.alter_column('TbKaMessage', 'deleted',
               existing_type=mysql.VARCHAR(length=1),
               type_=sa.CHAR(length=1),
               existing_nullable=True)
    op.drop_index('idx_ka_message_subject_sent', table_name='TbKaMessage')
    op.create_index('idx_ka_message_subject_sent', 'TbKaMessage', ['subject_id', sa.text('last_sent_at DESC')], unique=False)
    op.alter_column('TbSubject', 'deleted',
               existing_type=mysql.VARCHAR(length=1),
               type_=sa.CHAR(length=1),
               existing_nullable=True)


def downgrade() -> None:
    op.alter_column('TbSubject', 'deleted',
               existing_type=sa.CHAR(length=1),
               type_=mysql.VARCHAR(length=1),
               existing_nullable=True)
    op.drop_index('idx_ka_message_subject_sent', table_name='TbKaMessage')
    op.create_index('idx_ka_message_subject_sent', 'TbKaMessage', ['subject_id', 'last_sent_at'], unique=False)
    op.alter_column('TbKaMessage', 'deleted',
               existing_type=sa.CHAR(length=1),
               type_=mysql.VARCHAR(length=1),
               existing_nullable=True)
    op.alter_column('TbKaMessage', 'similar_id',
               existing_type=sa.CHAR(length=32),
               type_=mysql.VARCHAR(length=32),
               existing_nullable=False)
    op.alter_column('TbKaMessage', 'id',
               existing_type=sa.CHAR(length=32),
               type_=mysql.VARCHAR(length=32),
               existing_nullable=False)
