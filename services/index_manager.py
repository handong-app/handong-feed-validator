import os
import pickle
from datetime import datetime

from annoy import AnnoyIndex
from sqlalchemy.sql import text

from config.constants import LocalPath
from services.build_service import BuildService
from util.io_utils import output_ln


class IndexManager:
    @staticmethod
    def all_artifacts_exist() -> bool:
        """필수 아티팩트가 모두 존재하는지 확인"""
        required_files = [
            LocalPath.ANNOY_INDEX_LAST_14DAYS,
            LocalPath.TFIDF_VECTORIZER_LAST_14DAYS,
            LocalPath.LAST_14DAYS_DF
        ]
        return all(os.path.exists(file) for file in required_files)

    @staticmethod
    def is_outdated() -> bool:
        """Annoy 인덱스가 최신 상태인지 확인"""

        # 아티팩트가 없으면 outdated
        if not IndexManager.all_artifacts_exist():
            return True

        # 최근 14일치 데이터의 최신 업데이트 시간 가져오기 (예: DB에서)
        latest_data_update_time = IndexManager.get_latest_data_update_time()

        # 각 아티팩트의 최종 수정 시간 확인
        artifact_times = [
            os.path.getmtime(LocalPath.ANNOY_INDEX_LAST_14DAYS),
            os.path.getmtime(LocalPath.TFIDF_VECTORIZER_LAST_14DAYS),
            os.path.getmtime(LocalPath.LAST_14DAYS_DF)
        ]
        latest_artifact_time = max(artifact_times)

        output_ln(f'latest_artifact_time: {latest_artifact_time}')
        output_ln(f'latest_data_update_time: {latest_data_update_time}')

        # 아티팩트의 최종 수정 시간이 데이터보다 오래됐으면 outdated
        if abs(latest_artifact_time - latest_data_update_time) < 1e-9:
            # 소수점 이하까지 같으면 최신 상태
            return False
        else:
            # 소수점 이하가 다르면 비교해서 판단
            return latest_artifact_time < latest_data_update_time

    @staticmethod
    def get_latest_data_update_time() -> float:
        """DB에서 최근 14일치 데이터의 최신 업데이트 시간 가져오기"""

        # 예시: SQLAlchemy를 사용하여 DB에서 최신 업데이트 시간 가져오기
        from util.database import engine
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT MAX(updated_at) FROM TbKaMessage WHERE updated_at >= NOW() - INTERVAL 14 DAY")
            ).scalar()
        return result.timestamp() if result else datetime.now().timestamp()

    @staticmethod
    def ensure_index():
        """아티팩트가 outdated 상태라면 빌드"""
        if IndexManager.is_outdated():
            output_ln("🕒 Annoy 인덱스가 outdated 상태입니다. 다시 빌드합니다.")
            BuildService.build_annoy_index_last_14days()
        else:
            output_ln("✅ Annoy 인덱스가 최신 상태입니다. 빌드 스킵.")

    @staticmethod
    def load_tfidf_vectorizer():
        """TF-IDF 벡터화 모델 로드"""
        with open(LocalPath.TFIDF_VECTORIZER_LAST_14DAYS, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def load_annoy_index(vectorizer) -> "AnnoyIndex":
        """Annoy 인덱스 로드"""
        dimension = len(vectorizer.get_feature_names_out())
        annoy_index = AnnoyIndex(dimension, 'angular')
        annoy_index.load(LocalPath.ANNOY_INDEX_LAST_14DAYS)
        return annoy_index

    @staticmethod
    def load_last_14days_dataframe():
        """최근 14일 데이터 로드"""
        with open(LocalPath.LAST_14DAYS_DF, 'rb') as f:
            return pickle.load(f)