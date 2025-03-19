from enum import Enum as PyEnum

class LogType(PyEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    DEBUG = "DEBUG"

class LogMessage(PyEnum):
    VALIDATED = "유사도 검색 실행 완료"
    PROCESSED_AS_NEW_MESSAGE = "새로운 메시지로 처리됨"
    PROCESSED_AS_SIMILAR_MESSAGE = "유사 메시지로 처리됨"
    PROCESSED_AS_DUPLICATE_MESSAGE = "중복 메시지로 처리됨"

    SAVED = "DB에 저장됨"
    NOT_SAVED = "DB에 저장되지 않음"


class Status(PyEnum):
    CHECKED = "CHECKED"  # 거리 측정 완료
    WILL_BE_SAVED = "WILL_BE_SAVED"  # 신규 혹은 유사 메시지이므로 DB에 저장될 예정
    WILL_NOT_BE_SAVED = "WILL_NOT_BE_SAVED"  # 중복 메시지이므로 DB에 저장되지 않을 예정
    SAVED = "SAVED"  # DB에 저장됨
    NOT_SAVED = "NOT_SAVED"  # DB에 저장되지 않음
    ERROR = "ERROR" # 에러 발생

class CaseType(PyEnum):
    UNDETERMINED = "UNDETERMINED"  # 거리 측정만 된 상태로, 케이스 판정이 진행되지 않음
    NEW_MESSAGE = "NEW_MESSAGE"  # 새로운 메시지로 처리됨
    SIMILAR_MESSAGE = "SIMILAR_MESSAGE"  # 유사 메시지로 처리됨
    DUPLICATE_MESSAGE = "DUPLICATE_MESSAGE"  # 중복 메시지로 처리됨