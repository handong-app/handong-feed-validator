from sqlalchemy import Column, String, DateTime, BigInteger, Integer
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.dialects.mysql import INTEGER

from util.database import Base

def get_seoul_time():
    return datetime.now(ZoneInfo("Asia/Seoul"))

class TbKaMessage(Base):
    __tablename__ = "TbKaMessage"

    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    chat_id = Column(BigInteger, nullable=False)
    client_message_id = Column(BigInteger, nullable=False)
    room_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    message = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=get_seoul_time)
    last_sent_at = Column(Integer)
    deleted = Column(String(1), default="N")
    subject_id = Column(BigInteger, nullable=False)