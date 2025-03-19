from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from util.database import engine
from util.date_tool import convert_to_kst_datetime

def ensure_log_table():
    """log_validator 테이블이 없으면 생성"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS log_validator (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        timestamp DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6),
        chat_id BIGINT NOT NULL,
        log_type VARCHAR(50) NOT NULL,
        message TEXT NOT NULL,
        latest_artifact_time DATETIME(6),
        latest_data_update_time DATETIME(6),
        status VARCHAR(20) NOT NULL,
        distance FLOAT DEFAULT NULL,
        case_type VARCHAR(50) DEFAULT NULL,
        similar_message_id VARCHAR(32) DEFAULT NULL,
        subject_id VARCHAR(32) DEFAULT NULL,
        ip_address VARCHAR(45) DEFAULT NULL,
        user_id BIGINT NULL
    )
    """
    try:
        with engine.connect() as connection:
            connection.execute(text(create_table_sql))
            connection.commit()
    except ProgrammingError as e:
        print(f"❌ [ERROR] 테이블 생성 중 오류 발생: {e}")


def save_log(
    chat_id: int,
    log_type: str,
    message: str,
    latest_artifact_time: float = None,
    latest_data_update_time: float = None,
    status: str = None,
    distance: float = None,
    case_type: str = None,
    similar_message_id: str = None,
    subject_id: str = None,
    ip_address: str = None,
    user_id: int = None
):
    """로그를 DB에 저장"""

    ensure_log_table()

    latest_artifact_kst = convert_to_kst_datetime(latest_artifact_time)
    latest_data_update_kst = convert_to_kst_datetime(latest_data_update_time)

    try:
        with engine.connect() as connection:
            query = text("""
                INSERT INTO log_validator (
                    chat_id, log_type, message, 
                    latest_artifact_time, latest_data_update_time, status, 
                    distance, case_type, similar_message_id, subject_id,
                    ip_address, user_id
                ) VALUES (
                    :chat_id, :log_type, :message, 
                    :latest_artifact_time, :latest_data_update_time, :status, 
                    :distance, :case_type, :similar_message_id, :subject_id,
                    :ip_address, :user_id
                )
            """)

            connection.execute(query, {
                "chat_id": chat_id,
                "log_type": log_type,
                "message": message,
                "latest_artifact_time": latest_artifact_kst,
                "latest_data_update_time": latest_data_update_kst,
                "status": status,
                "distance": distance,
                "case_type": case_type,
                "similar_message_id": similar_message_id,
                "subject_id": subject_id,
                "ip_address": ip_address,
                "user_id": user_id
            })
            connection.commit()

    except SQLAlchemyError as e:
        print(f"❌ 로그 저장 실패: {str(e)}")
        with open("../log_error.log", "a") as f:
            from datetime import datetime
            f.write(f"[{datetime.now()}] 로그 저장 실패: {str(e)}\n")
