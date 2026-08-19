class ApiError(Exception):
    """A structured API error, serialised as {"code": ..., "message": ...}."""

    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)
