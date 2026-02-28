from sqlalchemy.ext.asyncio import create_async_engine

from app.adapters.postgres import PostgresFurnitureRepository
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.catalog import Catalog


def main():
    config = RootConfig()
    engine = create_async_engine(config.postgres.url())
    repository = PostgresFurnitureRepository(engine)
    catalog = Catalog(repository)
    asgi = ASGI(catalog)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
