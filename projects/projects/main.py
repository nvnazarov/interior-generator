if __name__ == "__main__":
    from projects.config import Config
    from projects.infra.uow import ProjectUnitOfWorkFactory
    from projects.api import API
    from projects.core.service import ProjectService

    config = Config()
    api = API(
        project_service=ProjectService(
            unit_of_work_factory=ProjectUnitOfWorkFactory(url=config.postgres.url()),
            max_projects_per_account=config.max_projects_per_account,
        ),
        header_with_account_id=config.header_with_account_id,
    )
    api.serve_http(host=config.host, port=config.port)
