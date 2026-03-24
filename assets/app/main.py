from app.adapters.minio import MinioStorage
from app.api.asgi import ASGI
from app.configs.root import RootConfig
from app.core.service import Service


def main():
    config = RootConfig()
    storage = MinioStorage(config.minio)
    service = Service(storage)
    asgi = ASGI(service)
    asgi.listen_and_serve(config.api.host, config.api.port)


if __name__ == "__main__":
    main()
