import uuid
from typing import List

from app.api.checks.schemas import DocType, ProgramType, SwaggerFile, Status
from database.models import DocumentModel, IssueModel, CheckModel
from s3 import s3
from settings import S3


def detect_doc_type(filename: str) -> str | None:
    filename = filename.lower()
    contract_names = ["contract", "dogovor", "договор"]
    act_names = ["act", "акт", "упд"]
    invoice_names = ["invoice", "счёт", "счет"]
    specification_names = ["specification", "спецификация"]
    for name in contract_names:
        if name in filename:
            return DocType.contract
    for name in act_names:
        if name in filename:
            return DocType.act
    for name in invoice_names:
        if name in filename:
            return DocType.invoice
    for name in specification_names:
        if name in filename:
            return DocType.specification
    return None


def check_all_doc_types_for_program(
        doc_list: List[DocumentModel], program_type: ProgramType, issue_list: List[IssueModel]
) -> Status:
    eng_to_rus = {
        DocType.act: "акт",
        DocType.specification: "спецификация",
        DocType.invoice: "счет",
        DocType.contract: "договор"
    }
    expected_types = [DocType.contract, DocType.invoice, DocType.act]
    if program_type == ProgramType.federal:
        expected_types.append(DocType.specification)

    for doc in doc_list:
        if doc.detected_type in expected_types:
            expected_types.remove(doc.detected_type)

    status = Status.approved if not expected_types else Status.rejected
    for doc_type in expected_types:
        issue_list.append(IssueModel(
            level="error",
            message=f"Отсутствует обязательный документ: {eng_to_rus[doc_type]}"
        ))
    return status


async def save_doc_to_s3(file: SwaggerFile, key: str):
    async with s3.client(
        service_name="s3",
        endpoint_url=S3.endpoint_url
    ) as s3_client:
        await s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=S3.bucket_name,
            Key=key
        )

async def check_docs(files: List[SwaggerFile], check_record: CheckModel):
    expected_file_extensions = ["pdf", "png", "jpg", "docx"]
    issue_list = []
    doc_list = []
    for file in files:
        if not file.filename:
            continue
        file_ext = file.filename.split('.')[-1].lower()
        doc_type = detect_doc_type(file.filename)
        file_size = file.size or 0
        if file_ext not in expected_file_extensions:
            issue_list.append(IssueModel(
                level="warning",
                message=f"Недопустимое расширение файла: {file.filename}",
                check_id=check_record.id
            ))
        elif not doc_type:
            issue_list.append(IssueModel(
                level="warning",
                message=f"Не удалось определить тип документа: {file.filename}",
                check_id=check_record.id
            ))
        elif file_size <= 0:
            issue_list.append(IssueModel(
                level="warning",
                message=f"Пустой файл: {file.filename}",
                check_id=check_record.id
            ))
        elif file_size / 1024 / 1024 > 20:
            issue_list.append(IssueModel(
                level="warning",
                message=f"Размер файла слишком большой: {file.filename}",
                check_id=check_record.id
            ))
        else:
            doc = DocumentModel(
                id=uuid.uuid4(),
                name=file.filename,
                detected_type=doc_type,
                size_kb=file_size / 1024,
                check_id=check_record.id
            )
            doc_list.append(doc)
            await save_doc_to_s3(file, f"{doc.id}.{file_ext}")

    status = check_all_doc_types_for_program(
        doc_list, check_record.program_type, issue_list
    )
    check_record.status = status
    check_record.issues = issue_list
    check_record.documents = doc_list

