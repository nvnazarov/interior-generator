if __name__ == "__main__":
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.adapters.postgres import PostgresUnitOfWork
    from app.api.asgi import ASGI
    from app.configs.root import RootConfig
    from app.core.service import Service

    config = RootConfig()
    engine = create_async_engine(config.postgres.url())
    uow = PostgresUnitOfWork(engine)
    asgi = ASGI(
        Service(
            uow,
            projects_limit=config.general.projects_limit,
            plans_limit=config.general.plans_limit,
        ),
        header_for_account_id=config.api.header_for_account_id,
    )
    asgi.listen_and_serve(host=config.api.host, port=config.api.port)
