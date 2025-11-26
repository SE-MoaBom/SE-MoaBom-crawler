import os
from pathlib import Path
from dotenv import load_dotenv

root = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=root / ".env", verbose=True)


class Config:
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "moabom")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "1234")

    @property
    def DB_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/app.log")

    # Crawler Configuration
    HEADLESS_MODE: bool = os.getenv("HEADLESS_MODE", "true").lower() == "true"
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    ACTION_DELAY: int = int(os.getenv("ACTION_DELAY", "300"))
    SCROLL_LIMIT: int = int(os.getenv("SCROLL_LIMIT", "100"))
    MAX_TABS: int = int(os.getenv("MAX_TABS", "5"))


config = Config()
