from fastapi import HTTPException

from app.api.schemas import Response404Schema, Response400Schema, Response422Schema


class Response404Error(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=404,
            detail=Response404Schema(message=message).model_dump()
        )

class Response400Error(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=400,
            detail=Response400Schema(message=message).model_dump()
        )


class Response422Error(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=422,
            detail=Response422Schema(message=message).model_dump()
        )