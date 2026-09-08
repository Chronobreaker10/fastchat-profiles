from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from config import Settings, settings
from logger import app_errors_logger
from models import Profile  # noqa: F401
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@dataclass
class PoolConfig:
    """Настройки пула подключения к базе данных"""

    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False
    echo_pool: bool = False
    pool_recycle: int = 1800
    pool_pre_ping: bool = True
    pool_timeout: int = 10


class DatabaseHelper:
    """Класс для работы с базой данных"""

    def __init__(self, url: str, pool_config: PoolConfig) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=pool_config.echo,
            echo_pool=pool_config.echo_pool,
            pool_size=pool_config.pool_size,
            max_overflow=pool_config.max_overflow,
            pool_pre_ping=pool_config.pool_pre_ping,
            pool_timeout=pool_config.pool_timeout,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @classmethod
    def from_settings(cls, config: Settings) -> DatabaseHelper:
        """Создаем экземпляр класса из настроек"""
        pool_config = PoolConfig(
            echo=config.database.echo,
            echo_pool=config.database.echo_pool,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_timeout=config.database.pool_timeout,
        )
        return cls(config.database.url, pool_config)

    @staticmethod
    async def set_isolation_level(session: AsyncSession, level: str) -> None:
        """Устанавливаем допустимый уровень изоляции транзакции"""
        valid_levels = {
            "READ UNCOMMITTED",
            "READ COMMITTED",
            "REPEATABLE READ",
            "SERIALIZABLE",
        }
        isolation_level = level.upper()
        if isolation_level not in valid_levels:
            message = (
                f"Неверно задан уровень изоляции транзакции: {isolation_level}. "
                f"Должен быть одним из {', '.join(valid_levels)}"
            )
            raise ValueError(message)
        await session.execute(
            text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}")
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        async with self.session_factory() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                app_errors_logger.error(e, exc_info=True)
                raise
            finally:
                await session.close()

    async def dispose(self) -> None:
        """Закрываем пул соединений с базой данных"""
        await self.engine.dispose()


db_helper = DatabaseHelper.from_settings(settings)
