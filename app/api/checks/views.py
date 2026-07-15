import uuid
from typing import List

from fastapi import APIRouter, Path, Depends, File, Form
from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.checks.helpers import check_docs
from app.api.checks.schemas import FullCheckResponse, ListCheckResponse, ProgramType, SwaggerFile
from app.api.responses import Response404Error, Response400Error
from app.api.schemas import Response400Schema, Response404Schema, Response422Schema
from database import get_session
from database.models import CheckModel

router = APIRouter(
    prefix="/checks",
    tags=["checks"],
)

@router.post(
    "/",
    responses={
        400: {"model": Response400Schema},
        422: {"model": Response422Schema},
    },
    summary="Send docs"
)
async def create_check_record(
        db_session: AsyncSession = Depends(get_session),
        program_type: ProgramType = Form(),
        files: List[SwaggerFile] = File(...)
) -> FullCheckResponse:
    if not files:
        raise Response400Error("Необходимо загрузить хотя бы один файл.")
    check_id = uuid.uuid4()
    check_record = CheckModel(
        id=check_id,
        program_type=program_type
    )
    await check_docs(files, check_record)

    db_session.add(check_record)
    await db_session.commit()

    check_record = await CheckModel.get_by_id(db_session, check_id)
    return FullCheckResponse(result=check_record)


@router.get(
    "/",
    responses={
        400: {"model": Response400Schema},
    },
    summary="Get list of all checks"
)
async def get_checks(
        db_session: AsyncSession = Depends(get_session),
        page_params: Params = Depends()
) -> ListCheckResponse:
    checks = await CheckModel.get_page(db_session, page_params) or []
    return ListCheckResponse(result=checks)

@router.get(
    "/{id}/",
    responses={
        400: {"model": Response400Schema},
        404: {"model": Response404Schema}
    },
    summary="Get checks by id"
)
async def get_check_by_id(
        db_session: AsyncSession = Depends(get_session),
        check_id: uuid.UUID = Path(alias="id")
) -> FullCheckResponse:
    check = await CheckModel.get_by_id(db_session, check_id)
    if check is None:
        raise Response404Error(message=f"Проверка с id {check_id} не найдена.")
    return FullCheckResponse(result=check)