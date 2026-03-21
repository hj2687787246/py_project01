from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from database import Base, engine
import models  # noqa: F401
from books import books as books_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(books_router, prefix="/book")


@app.get("/")
async def root():
    return {"message": "Hello (async)"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
