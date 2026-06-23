import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from app.config import settings


logger = logging.getLogger(__name__)

class MongoConnection:
    client: AsyncIOMotorClient | None = None

mongo = MongoConnection()

async def connect_to_mongo() -> None:
    mongo.client = AsyncIOMotorClient(settings.mongo_uri)
    logger.info("Conectado ao MongoDB em %s", settings.mongo_uri)

async def close_mongo_connection() -> None:
    if mongo.client is not None:
        mongo.client.close()
        logger.info("Conexão com o MongoDB encerrada")

def get_collection() -> AsyncIOMotorCollection:
    if mongo.client is None:
        raise RuntimeError("Conexão com o MongoDB não foi inicializada.")
    return mongo.client[settings.mongo_db_name][settings.mongo_collection]
