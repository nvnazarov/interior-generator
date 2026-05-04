import asyncio

from app.adapters.elastic import ElasticCatalog
from app.configs.root import RootConfig


async def migrate():
    config = RootConfig()
    elastic = ElasticCatalog(config.elastic.host, config.elastic.index)
    await elastic.ensure_index_exists()


if __name__ == "__main__":
    asyncio.run(migrate())
