"""empty message

Revision ID: 18794de38ad9
Revises: f0820e47fad9
Create Date: 2026-07-15 17:01:53.628955

"""
import datetime
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '18794de38ad9'
down_revision: Union[str, Sequence[str], None] = 'f0820e47fad9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    checks_table = sa.table(
        'checks',
        sa.column('id', sa.UUID),
        sa.column('status', sa.String),
        sa.column('program_type', sa.String),
        sa.column('extracted_data', postgresql.JSONB),
        sa.column('checked_at', sa.DateTime(timezone=True))
    )

    documents_table = sa.table(
        'documents',
        sa.column('id', sa.UUID),
        sa.column('name', sa.String),
        sa.column('detected_type', sa.String),
        sa.column('size_kb', sa.Integer),
        sa.column('created_at', sa.DateTime(timezone=True)),
        sa.column('check_id', sa.UUID)
    )

    issues_table = sa.table(
        'issues',
        sa.column('id', sa.UUID),
        sa.column('level', sa.String),
        sa.column('message', sa.String),
        sa.column('check_id', sa.UUID)
    )

    check_ids = [uuid.uuid4() for _ in range(6)]
    now = datetime.datetime.now(datetime.timezone.utc)

    checks_data = [
        {
            "id": check_ids[0],
            "status": "approved",
            "program_type": "regional",
            "extracted_data": {
                "contractor": "ИП Иванов И.И.",
                "amount": "450 000",
                "date": "10.05.2026",
                "subject": "Оказание маркетинговых услуг"
            },
            "checked_at": now - datetime.timedelta(days=5)
        },
        {
            "id": check_ids[1],
            "status": "rejected",
            "program_type": "federal",
            "extracted_data": {
                "contractor": "ООО 'Альфа'",
                "amount": "12 500 000",
                "date": "01.06.2026",
                "subject": "Поставка серверного оборудования"
            },
            "checked_at": now - datetime.timedelta(days=4)
        },
        {
            "id": check_ids[2],
            "status": "check_in_progress",
            "program_type": "federal",
            "extracted_data": None,
            "checked_at": now - datetime.timedelta(hours=2)
        },
        {
            "id": check_ids[3],
            "status": "rejected",
            "program_type": "regional",
            "extracted_data": {
                "contractor": "АО 'Вектор'",
                "amount": "890 000",
                "date": "25.05.2026",
                "subject": "Аренда нежилого помещения"
            },
            "checked_at": now - datetime.timedelta(days=3)
        },
        {
            "id": check_ids[4],
            "status": "approved",
            "program_type": "federal",
            "extracted_data": {
                "contractor": "ООО 'ТехАгро'",
                "amount": "1 250 000",
                "date": "15.03.2026",
                "subject": "Поставка минеральных удобрений"
            },
            "checked_at": now - datetime.timedelta(days=2)
        },
        {
            "id": check_ids[5],
            "status": "rejected",
            "program_type": "federal",
            "extracted_data": {
                "contractor": "ООО 'Сигма'",
                "amount": "3 100 000",
                "date": "12.04.2026",
                "subject": "Строительно-монтажные работы"
            },
            "checked_at": now - datetime.timedelta(days=1)
        }
    ]

    documents_data = [
        {"id": uuid.uuid4(), "name": "dogovor_regional.pdf", "detected_type": "contract", "size_kb": 250, "created_at": now, "check_id": check_ids[0]},
        {"id": uuid.uuid4(), "name": "schet_12.pdf", "detected_type": "invoice", "size_kb": 120, "created_at": now, "check_id": check_ids[0]},
        {"id": uuid.uuid4(), "name": "act_vipolnenih.pdf", "detected_type": "act", "size_kb": 180, "created_at": now, "check_id": check_ids[0]},

        {"id": uuid.uuid4(), "name": "main_contract.pdf", "detected_type": "contract", "size_kb": 1050, "created_at": now, "check_id": check_ids[1]},
        {"id": uuid.uuid4(), "name": "invoice_unpaid.pdf", "detected_type": "invoice", "size_kb": 95, "created_at": now, "check_id": check_ids[1]},
        {"id": uuid.uuid4(), "name": "delivery_act.docx", "detected_type": "act", "size_kb": 310, "created_at": now, "check_id": check_ids[1]},

        {"id": uuid.uuid4(), "name": "draft_contract.pdf", "detected_type": "contract", "size_kb": 450, "created_at": now, "check_id": check_ids[2]},
        {"id": uuid.uuid4(), "name": "draft_invoice.pdf", "detected_type": "invoice", "size_kb": 115, "created_at": now, "check_id": check_ids[2]},

        {"id": uuid.uuid4(), "name": "rent_agreement.pdf", "detected_type": "contract", "size_kb": 1200, "created_at": now, "check_id": check_ids[3]},
        {"id": uuid.uuid4(), "name": "invoice_rent.pdf", "detected_type": "invoice", "size_kb": 90, "created_at": now, "check_id": check_ids[3]},
        {"id": uuid.uuid4(), "name": "act_accept.pdf", "detected_type": "act", "size_kb": 140, "created_at": now, "check_id": check_ids[3]},
        {"id": uuid.uuid4(), "name": "huge_scan_archive.zip", "detected_type": "contract", "size_kb": 25000, "created_at": now, "check_id": check_ids[3]}, # Ошибка размера и формата!

        {"id": uuid.uuid4(), "name": "dogovor_agro_47.pdf", "detected_type": "contract", "size_kb": 142, "created_at": now, "check_id": check_ids[4]},
        {"id": uuid.uuid4(), "name": "specification_final.docx", "detected_type": "specification", "size_kb": 85, "created_at": now, "check_id": check_ids[4]},
        {"id": uuid.uuid4(), "name": "invoice_agro.pdf", "detected_type": "invoice", "size_kb": 110, "created_at": now, "check_id": check_ids[4]},
        {"id": uuid.uuid4(), "name": "act_agro_signed.pdf", "detected_type": "act", "size_kb": 195, "created_at": now, "check_id": check_ids[4]},

        {"id": uuid.uuid4(), "name": "stroy_contract.pdf", "detected_type": "contract", "size_kb": 2100, "created_at": now, "check_id": check_ids[5]},
        {"id": uuid.uuid4(), "name": "unknown_file_v1.png", "detected_type": "specification", "size_kb": 450, "created_at": now, "check_id": check_ids[5]},
        {"id": uuid.uuid4(), "name": "stroy_act_signed.pdf", "detected_type": "act", "size_kb": 180, "created_at": now, "check_id": check_ids[5]}
    ]

    issues_data = [
        {
            "id": uuid.uuid4(),
            "level": "error",
            "message": "Отсутствует обязательный документ: спецификация к договору.",
            "check_id": check_ids[1]
        },
        {
            "id": uuid.uuid4(),
            "level": "warning",
            "message": "Формат документа 'delivery_act.docx' допустим, но рекомендуется использовать PDF.",
            "check_id": check_ids[1]
        },

        {
            "id": uuid.uuid4(),
            "level": "error",
            "message": "Превышен максимальный размер файла 'huge_scan_archive.zip' (24.4 МБ из 20 МБ разрешенных).",
            "check_id": check_ids[3]
        },
        {
            "id": uuid.uuid4(),
            "level": "warning",
            "message": "Недопустимый формат архива '.zip' для файла 'huge_scan_archive.zip'.",
            "check_id": check_ids[3]
        },

        {
            "id": uuid.uuid4(),
            "level": "error",
            "message": "Отсутствует обязательный документ: счёт на оплату.",
            "check_id": check_ids[5]
        },
        {
            "id": uuid.uuid4(),
            "level": "warning",
            "message": "Не удалось определить тип документа по имени 'unknown_file_v1.png'. Используется значение по умолчанию.",
            "check_id": check_ids[5]
        },
        {
            "id": uuid.uuid4(),
            "level": "warning",
            "message": "Изображение 'unknown_file_v1.png' имеет низкое разрешение для распознавания текста.",
            "check_id": check_ids[5]
        }
    ]
    op.bulk_insert(checks_table, checks_data)
    op.bulk_insert(documents_table, documents_data)
    op.bulk_insert(issues_table, issues_data)


def downgrade() -> None:
    op.execute("TRUNCATE TABLE checks CASCADE;")
