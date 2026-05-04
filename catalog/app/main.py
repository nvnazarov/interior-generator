from app.adapters.elastic import ElasticCatalog
from app.api.server import Server
from app.configs.root import RootConfig
from app.core.service import Service


def main():
    config = RootConfig()
    catalog = ElasticCatalog(config.elastic.host, config.elastic.index)
    service = Service(catalog)
    server = Server(service)
    server.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
