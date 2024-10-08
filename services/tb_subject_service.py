from sqlalchemy import text
from sqlalchemy.orm import Session

from models import TbSubject
from schemas.validate_dto import ValidateDto


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

    @staticmethod
    def update_last_sent_info(session: Session, dto: ValidateDto.ValidateReqDto, subject_id: int):
        session.execute(text(
            """
            UPDATE TbSubject
            SET last_sent_at = :last_sent_at, last_sent_chat_id = :last_sent_chat_id
            WHERE id = :subject_id
            """
        ), {
            "last_sent_at": dto.sent_at,
            "last_sent_chat_id": dto.chat_id,
            "subject_id": subject_id
        })
        #  여기 update_at 최신화 하는거 넣어야함
        session.commit()