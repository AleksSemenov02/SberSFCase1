from pydantic import BaseModel, Field


class Response200Schema(BaseModel):
    success: bool = True
    message: str | None = "Success"
    result: BaseModel | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = "error"


class Response400Schema(ErrorResponse):
    message: str = Field(examples=["Bad Request"])


class Response404Schema(ErrorResponse):
    message: str = Field(examples=["Not Found"])


class Response422Schema(ErrorResponse):
    message: str = Field(examples=["Unprocessable Entity"])