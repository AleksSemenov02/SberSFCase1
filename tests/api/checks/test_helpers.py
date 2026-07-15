from dataclasses import dataclass
from typing import List, Optional

import pytest

from app.api.checks.schemas import DocType, ProgramType, Status
from app.api.checks.helpers import detect_doc_type, check_all_doc_types_for_program

@dataclass
class DocStub:
    detected_type: Optional[DocType]


class TestDetectDocType:

    @pytest.mark.parametrize(
        "filename, expected_type",
        [
            ("Договор_47.pdf", DocType.contract),
            ("contract_15.docx", DocType.contract),
            ("dogovor_postavki.pdf", DocType.contract),
            ("Акт_выполненных_работ.pdf", DocType.act),
            ("УПД_001.pdf", DocType.act),
            ("act_2024.png", DocType.act),
            ("Счет_на_оплату.pdf", DocType.invoice),
            ("счёт_003.jpg", DocType.invoice),
            ("invoice_88.pdf", DocType.invoice),
            ("specification_v2.docx", DocType.specification),
        ],
    )
    def test_detects_known_doc_types(self, filename, expected_type):
        assert detect_doc_type(filename) == expected_type

    def test_case_insensitive_detection(self):
        assert detect_doc_type("ДОГОВОР_47.PDF") == DocType.contract

    def test_unrecognized_filename_returns_none(self):
        assert detect_doc_type("scan_0041.jpg") is None

    def test_empty_filename_returns_none(self):
        assert detect_doc_type("") is None

    def test_contract_priority_when_multiple_keywords_present(self):
        assert detect_doc_type("contract_act_combo.pdf") == DocType.contract


class TestCheckAllDocTypesForProgram:

    def test_federal_full_package_is_approved(self):
        docs = [
            DocStub(DocType.contract),
            DocStub(DocType.specification),
            DocStub(DocType.invoice),
            DocStub(DocType.act),
        ]
        issues = []
        status = check_all_doc_types_for_program(docs, ProgramType.federal, issues)
        assert status == Status.approved
        assert issues == []

    def test_federal_missing_specification_is_rejected(self):
        docs = [
            DocStub(DocType.contract),
            DocStub(DocType.invoice),
            DocStub(DocType.act),
        ]
        issues = []
        status = check_all_doc_types_for_program(docs, ProgramType.federal, issues)
        assert status == Status.rejected
        assert len(issues) == 1
        assert issues[0].level == "error"
        assert "спецификация" in issues[0].message

    def test_regional_full_package_is_approved(self):
        docs = [
            DocStub(DocType.contract),
            DocStub(DocType.invoice),
            DocStub(DocType.act),
        ]
        issues = []
        status = check_all_doc_types_for_program(docs, ProgramType.regional, issues)
        assert status == Status.approved
        assert issues == []

    def test_regional_missing_contract_is_rejected(self):
        docs = [
            DocStub(DocType.invoice),
            DocStub(DocType.act),
        ]
        issues = []
        status = check_all_doc_types_for_program(docs, ProgramType.regional, issues)
        assert status == Status.rejected
        assert len(issues) == 1
        assert "договор" in issues[0].message

    def test_empty_doc_list_is_rejected_with_all_errors(self):
        issues = []
        status = check_all_doc_types_for_program([], ProgramType.federal, issues)
        assert status == Status.rejected
        assert len(issues) == 4
        assert all(issue.level == "error" for issue in issues)

    def test_regional_missing_two_docs_produces_two_errors(self):
        docs = [DocStub(DocType.contract)]
        issues = []
        status = check_all_doc_types_for_program(docs, ProgramType.regional, issues)
        assert status == Status.rejected
        assert len(issues) == 2
        messages = " ".join(issue.message for issue in issues)
        assert "счет" in messages
        assert "акт" in messages

    def test_duplicate_doc_types_do_not_satisfy_multiple_requirements(self):
        docs = [
            DocStub(DocType.contract),
            DocStub(DocType.contract),
            DocStub(DocType.invoice),
            DocStub(DocType.act),
        ]
        issues = []
        status = check_all_doc_types_for_program(docs, ProgramType.federal, issues)
        assert status == Status.rejected
        assert len(issues) == 1
        assert "спецификация" in issues[0].message

    def test_unrelated_doc_type_none_is_ignored(self):
        docs = [
            DocStub(None),
            DocStub(DocType.contract),
            DocStub(DocType.invoice),
            DocStub(DocType.act),
        ]
        issues = []
        status = check_all_doc_types_for_program(docs, ProgramType.regional, issues)
        assert status == Status.approved
        assert issues == []