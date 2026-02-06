if __name__ == "__main__":
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.adapters.postgres import PostgresUnitOfWork
    from app.api.asgi import ASGI
    from app.config import Config
    from app.core.service import Service

    config = Config()
    engine = create_async_engine(config.postgres.url())
    uow = PostgresUnitOfWork(engine)
    asgi = ASGI(
        Service(
            uow,
            projects_limit=config.projects_limit,
            plans_limit=config.plans_limit,
        ),
        header_for_account_id=config.header_for_account_id,
    )
    asgi.listen_and_serve(host=config.host, port=config.port)
