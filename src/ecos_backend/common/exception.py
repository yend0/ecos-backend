from fastapi import HTTPException


class BadRequestException(HTTPException):
    def __init__(self, detail: str) -> None:
        super(BadRequestException, self).__init__(status_code=400, detail=detail)


class UnauthorizedExcetion(HTTPException):
    def __init__(self, detail: str) -> None:
        super(UnauthorizedExcetion, self).__init__(status_code=401, detail=detail)


class UnsupportedMediaTypeExcetion(HTTPException):
    def __init__(self, detail: str) -> None:
        super(UnsupportedMediaTypeExcetion, self).__init__(
            status_code=415, detail=detail
        )


class ForbiddenExcetion(HTTPException):
    def __init__(self, detail: str) -> None:
        super(ForbiddenExcetion, self).__init__(status_code=403, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str) -> None:
        super(NotFoundException, self).__init__(status_code=404, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str) -> None:
        super(ConflictException, self).__init__(status_code=409, detail=detail)


class PayloadTooLargeException(HTTPException):
    def __init__(self, detail: str) -> None:
        super(PayloadTooLargeException, self).__init__(status_code=413, detail=detail)


class ValidationException(HTTPException):
    def __init__(self, detail: str) -> None:
        super(ValidationException, self).__init__(status_code=422, detail=detail)


class InternalServerException(HTTPException):
    def __init__(self, detail: str) -> None:
        super(InternalServerException, self).__init__(status_code=500, detail=detail)
