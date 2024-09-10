from datetime import datetime
from sqlalchemy.orm import Session

from models import TbSubject


class TbSubjectService:
    @staticmethod
    def create_new_subject(session: Session, last_sent_at: int, last_sent_chat_id: int) -> int:
        try:
            new_subject = TbSubject(
                last_sent_at = last_sent_at,
                last_sent_chat_id = last_sent_chat_id,
            )
            session.add(new_subject)
            session.commit()
            return new_subject.id
        except Exception as e:
            session.rollback()
            print(f"Subject 생성 중 오류 발생: {e}")
            raise