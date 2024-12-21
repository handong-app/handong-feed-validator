class LocalPath:
    ARTIFACTS = './artifacts'
    ANNOY_INDEX_ALL = './artifacts/annoy_index_all.ann'
    TFIDF_VECTORIZER_ALL = './artifacts/tfidf_vectorizer_all.pkl'
    ANNOY_INDEX_LAST_14DAYS = './artifacts/annoy_index_last_14days.ann'
    TFIDF_VECTORIZER_LAST_14DAYS = './artifacts/tfidf_vectorizer_last_14days.pkl'

class DatabaseConfig:
    GET_TbKaMessage_LAST_14DAYS = "SELECT * FROM TbKaMessage WHERE created_at >= NOW() - INTERVAL 14 DAY"