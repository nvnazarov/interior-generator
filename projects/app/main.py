if __name__ == "__main__":
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.api import API
    from app.api.idempotency import IdempotencyProvider
    from app.config import Config
    from app.core.plan.service import PlanService
    from app.core.project.service import ProjectService
    from app.core.shell.service import ShellService
    from app.infra.plan import PlansUnitOfWork
    from app.infra.project import ProjectsUnitOfWork
    from app.infra.shell import ShellsUnitOfWork

    config = Config()
    engine = create_async_engine(config.postgres.url())
    api = API(
        plan_service=PlanService(
            lambda: PlansUnitOfWork(engine),
            max_plans_per_project=config.max_plans_per_project,
        ),
        shell_service=ShellService(
            lambda: ShellsUnitOfWork(engine),
            max_shells_per_account=config.max_shells_per_account,
        ),
        project_service=ProjectService(
            lambda: ProjectsUnitOfWork(engine),
            max_projects_per_account=config.max_projects_per_account,
        ),
        idempotency_provider=IdempotencyProvider(),
        header_with_account_id=config.header_with_account_id,
    )
    api.serve_http(host=config.host, port=config.port)
