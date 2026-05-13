import numpy as np

from app.core.models import Plan, Project


class Scene:
    _joins: np.ndarray[tuple[int, int], np.dtype[np.float64]]
    _walls: dict[int, list[int]]

    def __init__(self, project: Project, plan: Plan):
        self._joins = np.zeros((10, 2))
