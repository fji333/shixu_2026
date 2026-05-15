from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/gov_ai_assistant"
BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "政务智能问答系统"
    app_env: str = "development"
    database_url: str = DEFAULT_DATABASE_URL
    llm_enable: bool = False
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""
    llm_timeout: int = 30
    vector_db_path: str = "./data/vector_db"

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
