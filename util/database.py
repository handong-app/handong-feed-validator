import os
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')
DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 모든 모델의 부모
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_insert(session, message_id, chat_id, client_message_id, room_id, sent_at, user_id, message, current_time, duplicate_count, original_id):
    try:
        session.execute(text(
            """
            INSERT INTO mydb_TbKaFeed 
            (id, chatId, clientMessageId, roomId, sentAt, userId, message, createdDate, modifiedDate, duplicate_count, original_message_id, deleted)
            VALUES (:id, :chatId, :clientMessageId, :roomId, :sentAt, :userId, :message, :createdDate, :modifiedDate, :duplicate_count, :original_message_id, :deleted)
            """
        ), {
            "id": message_id,
            "chatId": chat_id,
            "clientMessageId": client_message_id,
            "roomId": room_id,
            "sentAt": sent_at,
            "userId": user_id,
            "message": message,
            "createdDate": current_time,
            "modifiedDate": current_time,
            "duplicate_count": duplicate_count,
            "original_message_id": original_id,
            "deleted": "N"
        })
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"데이터 삽입 중 문제 발생: {e}")
    finally:
        print("데이터가 성공적으로 삽입되었습니다.")
        session.close()