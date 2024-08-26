import logging

import motor
from beanie import init_beanie

from app.settings import DATABASE_URL

logger = logging.getLogger(__name__)


_beanie_model_list = []


def beanie_model_register(cls):
    if cls in _beanie_model_list:
        raise KeyError("Already a registered model.")

    _beanie_model_list.append(cls)
    return cls


async def init_db() -> motor.motor_asyncio.AsyncIOMotorClient:
    logger.info("Initializing database connection %s", DATABASE_URL)

    client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
    await init_beanie(
        database=client.get_default_database(),
        document_models=_beanie_model_list,
        allow_index_dropping=True,
    )

    return client
