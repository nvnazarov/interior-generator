class ProjectNotFoundError(RuntimeError):
    pass


class ProjectsPerAccountLimitExceededError(RuntimeError):
    pass


class PlansPerProjectLimitExceededError(RuntimeError):
    pass


class PlanVersionConflict(RuntimeError):
    pass
