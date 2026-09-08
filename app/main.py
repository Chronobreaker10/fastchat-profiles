from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from config import settings
from database import db_helper
from errors import setup_exceptions
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares import RequestContextMiddleware
from router import router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    yield
    await db_helper.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.api_config.title,
    description=settings.api_config.description,
    version=settings.api_config.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix=settings.api_config.prefix)
setup_exceptions(app)
app.add_middleware(RequestContextMiddleware)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.run_config.host, port=settings.run_config.port)
