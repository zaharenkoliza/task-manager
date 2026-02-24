from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)

    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = deep_merge(result[key], val)
        else:
            result[key] = val

    return result


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data if isinstance(data, dict) else {}


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    name: str = "tasks_db"

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseModel):
    debug: bool = Field(default=False)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    class Config:
        arbitrary_types_allowed = True


def build_settings() -> Settings:
    config_dir = BASE_DIR.parent / "config"

    default_config = load_yaml(config_dir / "default.yaml")
    local_config = load_yaml(config_dir / "local.yaml")

    merged = deep_merge(default_config, local_config)

    return Settings(**merged)


settings = build_settings()
