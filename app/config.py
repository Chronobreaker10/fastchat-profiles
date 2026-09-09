from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEYS_DIR = BASE_DIR / "secret_keys"

Path(SECRET_KEYS_DIR).mkdir(
    parents=True,
    exist_ok=True,
)


class ApiConfig(BaseModel):
    version: str = "1.0.0"
    prefix: str = "/v1"
    title: str = "FastChat Profiles"
    description: str = "API для работы с профилями мессенджера Fast Chat"


class CorsConfig(BaseModel):
    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://fastchat_proxy:80",
            "https://fastchat_proxy:443",
        ]
    )


class RunConfig(BaseModel):
    scheme: Literal["http", "https"]
    host: str = "localhost"
    port: int = 8002


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str
    password: str
    name: str = "fastchat"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    pool_timeout: int = 10

    @cached_property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0


class CacheConfig(BaseModel):
    profiles_key_prefix: str = "profiles"
    profiles_ttl: int = 60
    max_age: int


class SecurityConfig(BaseModel):
    access_token_cookie_name: str = "fastchat_access_token"
    algorithm: str
    api_key: str
    api_key_header: str = "x-api-key"

    @cached_property
    def public_key(self) -> str:
        with Path.open(SECRET_KEYS_DIR / "public.pem") as file:
            return file.read()


class Settings(BaseSettings):
    database: DatabaseConfig
    redis: RedisConfig
    security: SecurityConfig
    env: Literal["prod", "dev", "test"] = "dev"
    cors: CorsConfig = Field(default_factory=CorsConfig)
    run_config: RunConfig
    api_config: ApiConfig = Field(default_factory=ApiConfig)
    cache_config: CacheConfig = Field(default_factory=CacheConfig)
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
