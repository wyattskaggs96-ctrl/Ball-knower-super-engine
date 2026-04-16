from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    db_path: str = Field(default="./data/ball_knower.db")
    export_dir: str = Field(default="./data/exports")
    score_threshold: float = Field(default=65.0)

    enable_rss: bool = Field(default=True)
    enable_reddit: bool = Field(default=True)
    enable_manual: bool = Field(default=True)

    use_llm: bool = Field(default=False)
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4o-mini")
    openai_api_key: str = Field(default="")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=os.getenv("BALL_KNOWER_DB_PATH", "./data/ball_knower.db"),
            export_dir=os.getenv("BALL_KNOWER_EXPORT_DIR", "./data/exports"),
            score_threshold=float(os.getenv("BALL_KNOWER_SCORE_THRESHOLD", "65")),
            enable_rss=_as_bool(os.getenv("BALL_KNOWER_ENABLE_RSS"), True),
            enable_reddit=_as_bool(os.getenv("BALL_KNOWER_ENABLE_REDDIT"), True),
            enable_manual=_as_bool(os.getenv("BALL_KNOWER_ENABLE_MANUAL"), True),
            use_llm=_as_bool(os.getenv("BALL_KNOWER_USE_LLM"), False),
            llm_provider=os.getenv("BALL_KNOWER_LLM_PROVIDER", "openai"),
            llm_model=os.getenv("BALL_KNOWER_LLM_MODEL", "gpt-4o-mini"),
            openai_api_key=os.getenv("BALL_KNOWER_OPENAI_API_KEY", ""),
        )

    def ensure_directories(self) -> None:
        Path(self.export_dir).mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
