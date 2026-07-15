import datetime
import uuid
from typing import List, Optional, Dict, Any

from fastapi_pagination import Params, Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Integer, String, UUID, DateTime, func, ForeignKey, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from database import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    detected_type: Mapped[str] = mapped_column(String(16), nullable=False)
    size_kb: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())

    # foreign keys
    check_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("checks.id"), nullable=False)

    # relations
    checks: Mapped["CheckModel"] = relationship("CheckModel", back_populates="documents")

class IssueModel(Base):
    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)

    # foreign keys
    check_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("checks.id"), nullable=False)

    # relations
    checks: Mapped["CheckModel"] = relationship("CheckModel", back_populates="issues")


class CheckModel(Base):
    __tablename__ = "checks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    program_type: Mapped[str] = mapped_column(String(16), nullable=False)
    extracted_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True, server_default="null")
    checked_at: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False, server_default=func.now())

    # relations
    documents: Mapped[List["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="checks", cascade="all, delete-orphan"
    )
    issues: Mapped[List["IssueModel"]] = relationship(
        "IssueModel", back_populates="checks", cascade="all, delete-orphan"
    )

    @classmethod
    async def get_by_id(cls, db_session: AsyncSession, check_id: uuid.UUID) -> Optional["CheckModel"]:
        query = select(cls).where(cls.id == check_id).options(
            selectinload(cls.documents),
            selectinload(cls.issues)
        )
        result = await db_session.execute(query)
        task = result.scalar()
        return task

    @classmethod
    async def get_page(cls, db_session: AsyncSession, page_params: Params) -> Page:
        documents_count_subq = (
            select(func.count(DocumentModel.id))
            .where(DocumentModel.check_id == cls.id)
            .scalar_subquery()
            .label("documents_count")
        )
        query = select(cls, documents_count_subq).order_by(cls.checked_at.desc())

        def transform_results(rows):
            paginated_checks = []
            for check, count in rows:
                check.documents_count = count
                paginated_checks.append(check)
            return paginated_checks

        tasks = await paginate(
            db_session,query,page_params,transformer=transform_results
        )
        return tasks
