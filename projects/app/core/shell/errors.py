class ShellsPerAccountLimitExceededError(RuntimeError):
    pass


class ShellVersionConflictError(RuntimeError):
    pass


class ShellNotFoundError(RuntimeError):
    pass


class ShellPatchError(RuntimeError):
    pass
