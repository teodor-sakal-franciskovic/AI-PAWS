class ApiError(Exception):
    """A structured API error, serialised as {"code": ..., "message": ..., "data": ...}."""

    def __init__(self, status_code: int, code: str, message: str, data=None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)
