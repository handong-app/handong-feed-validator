from sqlalchemy import Column, String, DateTime, BigInteger, Integer
from util.database import Base
from util.date_tool import get_seoul_time

class TbSubject(Base):
    __tablename__ = "TbSubject"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=get_seoul_time)
    updated_at = Column(DateTime, default=get_seoul_time, onupdate=get_seoul_time)
    last_sent_at = Column(Integer)
    last_sent_chat_id = Column(BigInteger)
    deleted = Column(String(1), default="N")
    # priority_value
    # is_ban
