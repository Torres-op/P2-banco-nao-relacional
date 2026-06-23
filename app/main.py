import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import close_mongo_connection, connect_to_mongo
from app.routers import pedidos


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title=settings.app_name,
    description=(
        "API para cadastro e consulta de pedidos. Persistindo no MongoDB e com serviços de mensageria com Kafka e RabbitMQ"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(pedidos.router)

@app.get("/health", tags=["Infra"], summary="Verificação de saúde")
async def health() -> dict:
    return {"status": "ok"}
