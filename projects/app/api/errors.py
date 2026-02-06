from fastapi import HTTPException, status


class HTTPProjectsLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail="projects limit exceeded")


class HTTPProjectNotFound(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, detail="project not found")


class HTTPPlansLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail="plans limit exceeded")


class HTTPPlanNotFound(HTTPException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, detail="plan not found")
