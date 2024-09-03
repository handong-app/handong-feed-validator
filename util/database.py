import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
