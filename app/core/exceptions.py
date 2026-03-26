"""Custom exception hierarchy."""


class AppError(Exception):
    """Base application error."""
    status_code: int = 500
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404

class ValidationError(AppError):
    status_code = 422

class AuthError(AppError):
    status_code = 401

class EnvError(AppError):
    status_code = 400

class GraderError(AppError):
    status_code = 500

class RAGError(AppError):
    status_code = 500
