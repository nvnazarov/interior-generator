from sqlalchemy.ext.asyncio import create_async_engine

from app.adapters.postgres import PostgresUnitOfWorkFactory
from app.api.server import Server
from app.configs.root import RootConfig
from app.core.service import Service


def main():
    config = RootConfig()
    engine = create_async_engine(config.postgres.url())
    uow = PostgresUnitOfWorkFactory(engine)
    service = Service(
        uow,
        projects_limit=config.general.projects_limit,
        plans_limit=config.general.plans_limit,
    )
    server = Server(service, account_header=config.api.account_header)
    server.listen_and_serve(host=config.api.host, port=config.api.port)


if __name__ == "__main__":
    main()
