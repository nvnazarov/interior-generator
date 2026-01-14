class PlansPerProjectLimitExceededError(RuntimeError):
    pass


class PlanNotFoundError(RuntimeError):
    pass


class PlanVersionConflictError(RuntimeError):
    pass


class PlanPatchError(RuntimeError):
    pass
