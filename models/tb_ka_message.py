from sqlalchemy import Column, String, DateTime, BigInteger, Integer
import uuid

from util.date_tool import get_seoul_time
from util.database import Base


class TbKaMessage(Base):
    __tablename__ = "TbKaMessage"

    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    chat_id = Column(BigInteger, nullable=False)
    client_message_id = Column(BigInteger, nullable=False)
    room_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    message = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=get_seoul_time)
    updated_at = Column(DateTime, default=get_seoul_time, onupdate=get_seoul_time)
    last_sent_at = Column(Integer)
    deleted = Column(String(1), default="N")
    subject_id = Column(BigInteger, nullable=False)