from sqlalchemy import Column, String, DateTime, BigInteger
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from util.database import Base

def get_seoul_time():
    return datetime.now(ZoneInfo("Asia/Seoul"))

class TbKaMessage(Base):
    __tablename__ = "TbKaMessage"

    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace('-', ''))
    message = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=get_seoul_time)
    last_sent_at = Column(DateTime)
    subject_id = Column(BigInteger, nullable=False)