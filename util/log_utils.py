from sqlalchemy import text
from util.database import engine
from util.date_tool import convert_to_kst_datetime


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

    latest_artifact_kst = convert_to_kst_datetime(latest_artifact_time)
    latest_data_update_kst = convert_to_kst_datetime(latest_data_update_time)

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