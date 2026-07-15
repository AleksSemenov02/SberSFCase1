import uuid
from datetime import datetime
from enum import Enum
from typing import List, Literal, Any, Dict, Optional, Annotated

from fastapi import UploadFile
from fastapi_pagination import Page
from pydantic import BaseModel, computed_field, Field, ConfigDict, WithJsonSchema

from app.api.schemas import Response200Schema


SwaggerFile = Annotated[
    UploadFile,
    WithJsonSchema({"type": "string", "format": "binary"})
]

class Status(str, Enum):
    approved = "approved"
    rejected = "rejected"
    check = "check_in_progress"


class DocType(str, Enum):
    contract = "contract"
    specification = "specification"
    invoice = "invoice"
    act = "act"


class ProgramType(str, Enum):
    federal = "federal"
    regional = "regional"


class IssueSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: Literal["error", "warning"]
    message: str


class DocsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    detected_type: DocType
    size_kb: int


class BaseCheckSchema(BaseModel):
    check_id: uuid.UUID = Field(validation_alias="id")
    status: Status
    checked_at: datetime


class CheckSchema(BaseCheckSchema):
    model_config = ConfigDict(from_attributes=True)

    program_type: ProgramType
    documents_count: int


class FullCheckSchema(BaseCheckSchema):
    model_config = ConfigDict(from_attributes=True)

    issues: List[IssueSchema]
    documents: List[DocsSchema]
    extracted: Optional[Dict[str, Any]] = Field(validation_alias="extracted_data")

    @computed_field
    def status_label(self) -> str:
        if self.status == "check_in_progress":
            return "Проверка выполняется"

        has_errors = any(issue.level == "error" for issue in self.issues)
        if has_errors or self.status == "rejected":
            return "Нельзя заявлять в банк"
        return "Успешно проверено"

    @computed_field
    def reason(self) -> Optional[str]:
        errors = [issue.message for issue in self.issues if issue.level == "error"]
        return errors[0] if errors else None


class FullCheckResponse(Response200Schema):
    result: FullCheckSchema


class ListCheckResponse(Response200Schema):
    result: Page[CheckSchema]