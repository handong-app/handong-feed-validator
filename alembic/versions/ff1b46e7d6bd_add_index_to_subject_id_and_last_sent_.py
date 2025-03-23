"""add index to subject_id and last_sent_at in tbkamessage

Revision ID: ff1b46e7d6bd
Revises: 347339a2659e
Create Date: 2025-03-23 16:26:55.654956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff1b46e7d6bd'
down_revision: Union[str, None] = '347339a2659e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index(
        'idx_ka_message_subject_sent',
        'TbKaMessage',
        ['subject_id', 'last_sent_at'],
        unique=False
    )


def downgrade():
    op.drop_index('idx_ka_message_subject_sent', table_name='TbKaMessage')
