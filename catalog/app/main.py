from sqlalchemy.ext.asyncio import create_async_engine

from app.adapters.postgres import PostgresFurnitureRepository
from app.api import API
from app.config import Config
from app.core.catalog import Catalog


def main():
    config = Config()
    engine = create_async_engine(config.postgres.url())
    repository = PostgresFurnitureRepository(engine)
    catalog = Catalog(repository)
    api = API(catalog)
    api.serve_http(config.host, config.port)


if __name__ == "__main__":
    main()
