"""add is_tag_assigned column to TbSubject

Revision ID: e5492ed75525
Revises: ff1b46e7d6bd
Create Date: 2025-04-28 20:41:36.432397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'e5492ed75525'
down_revision: Union[str, None] = 'ff1b46e7d6bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('TbKaMessage', 'similar_id',
               existing_type=mysql.VARCHAR(length=32),
               nullable=False)
    op.alter_column('TbKaMessage', 'deleted',
               existing_type=mysql.CHAR(length=1),
               type_=sa.String(length=1),
               existing_nullable=True)

    op.create_index('idx_ka_message_subject_sent', 'TbKaMessage', ['subject_id', sa.text('last_sent_at DESC')], unique=False)
    op.add_column('TbSubject', sa.Column('is_tag_assigned', sa.Boolean(), nullable=True))
    op.alter_column('TbSubject', 'deleted',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.String(length=1),
               existing_nullable=True)


def downgrade() -> None:
    op.alter_column('TbSubject', 'deleted',
               existing_type=sa.String(length=1),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)
    op.drop_column('TbSubject', 'is_tag_assigned')
    op.drop_index('idx_ka_message_subject_sent', table_name='TbKaMessage')
    op.create_index('idx_ka_message_subject_sent', 'TbKaMessage', ['subject_id', 'last_sent_at'], unique=False)
    op.alter_column('TbKaMessage', 'deleted',
               existing_type=sa.String(length=1),
               type_=mysql.CHAR(length=1),
               existing_nullable=True)
    op.alter_column('TbKaMessage', 'similar_id',
               existing_type=mysql.VARCHAR(length=32),
               nullable=True)
