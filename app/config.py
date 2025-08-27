from typing import Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用配置
    app_name: str = "Chatbot MVP"
    host: str = "127.0.0.1"
    port: int = 8000

    # 数据库配置
    database_url: str = "mysql+pymysql://root:root@localhost:3307/q3demo"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Milvus配置
    MILVUS_HOST: str = "127.0.0.1"
    MILVUS_PORT: str = "19530"
    MILVUS_DB: str = "q3demo"
    MILVUS_ALIAS: str = "q3"
    MILVUS_COLLECTION: str = "faq_qa"
    
    # 语义搜索配置
    SEMANTIC_MODEL: str = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = 0.75
    SEARCH_TOP_K: int = 3

    # 会话配置
    session_ttl_minutes: int = 30
    max_session_turns: int = 10

settings = Settings()