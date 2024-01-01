from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.database import Base, engine
from app.routers import users, items

description = """
Example API to demonstrate restricted routes
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title='Restricted routes example API',
    description=description,
    version="1.0.0",
    docs_url="/v1/docs",
    redoc_url=None,
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(items.router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
