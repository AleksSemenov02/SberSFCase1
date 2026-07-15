from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.checks.views import router
from s3.helpers import ensure_bucket_exists
from settings import S3


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await ensure_bucket_exists(S3.bucket_name)
    yield
    pass

app = FastAPI(
    title="SberSFCase1 API",
    lifespan=lifespan
)

app.include_router(router)
