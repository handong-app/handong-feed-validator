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
    def update_last_sent_at(session: Session, dto: ValidateDto.ValidateReqDto, subject_id: int):
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

        session.commit()

    @staticmethod
    def update_last_sent_chat(session: Session, chat_id: int, subject_id: int, sent_at: int):
        session.execute(text(
            """
            UPDATE TbSubject
            SET last_sent_at = :last_sent_at, last_sent_chat_id = :last_sent_chat_id
            WHERE id = :subject_id
            """
        ), {
            "last_sent_at": sent_at,
            "last_sent_chat_id": chat_id,
            "subject_id": subject_id
        })

        session.commit()