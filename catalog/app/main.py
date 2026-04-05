from app.adapters.elastic import ElasticFurnitureRepository
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.catalog import Catalog


def main():
    config = RootConfig()
    repository = ElasticFurnitureRepository(config.elastic.host, config.elastic.index)
    catalog = Catalog(repository)
    asgi = ASGI(catalog)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
