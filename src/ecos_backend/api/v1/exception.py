from fastapi import HTTPException


class BadRequestException(HTTPException):
    def __init__(self) -> None:
        super(BadRequestException, self).__init__(status_code=400, detail="Bad Request")


class UnauthorizedExcetion(HTTPException):
    def __init__(self) -> None:
        super(UnauthorizedExcetion, self).__init__(
            status_code=401, detail="Unauthorized"
        )


class UnsupportedMediaTypeExcetion(HTTPException):
    def __init__(self) -> None:
        super(UnsupportedMediaTypeExcetion, self).__init__(
            status_code=415, detail="Unsupported Media Type"
        )


class ForbiddenExcetion(HTTPException):
    def __init__(self) -> None:
        super(ForbiddenExcetion, self).__init__(status_code=403, detail="Forbidden")


class NotFoundException(HTTPException):
    def __init__(self) -> None:
        super(NotFoundException, self).__init__(status_code=404, detail="Not Found")


class ConflictException(HTTPException):
    def __init__(self) -> None:
        super(ConflictException, self).__init__(status_code=409, detail="Conflict")


class InternalServerException(HTTPException):
    def __init__(self, detail: str) -> None:
        super(InternalServerException, self).__init__(status_code=500)
        self._detail: str = detail

    def __str__(self) -> str:
        return self._detail
