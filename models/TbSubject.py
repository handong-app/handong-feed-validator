from sqlalchemy import Column, String, DateTime, BigInteger, Integer
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from util.database import Base

def get_seoul_time():
    return datetime.now(ZoneInfo("Asia/Seoul"))

class TbSubject(Base):
    __tablename__ = "TbSubject"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=get_seoul_time)
    last_sent_at = Column(Integer)
    last_sent_tb_ka_message_id = Column(String(32))
    deleted = Column(String(1), default="N")
    # priority_value
    # is_ban
