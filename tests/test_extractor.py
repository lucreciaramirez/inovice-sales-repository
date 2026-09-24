from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from invoice_summary.extractor import (
    InvoiceParseError,
    extract_folder,
    parse_amount,
    parse_invoice_text,
)

SAMPLES = Path(__file__).resolve().parent.parent / "samples"

SAMPLE_TEXT = """FACTURA C
Comp. Nro: 00003 00000123
Fecha de Emisión: 15/03/2026
30000000019
Cliente Demo S.A.
Importe Total: $ 12.345,67
"""


def test_parse_amount_handles_argentine_format():
    assert parse_amount("12.345,67") == Decimal("12345.67")
    assert parse_amount("1.234.567,00") == Decimal("1234567.00")
    assert parse_amount("500,5") == Decimal("500.5")
    assert parse_amount("800") == Decimal("800")


def test_parse_amount_rejects_garbage():
    with pytest.raises(ValueError):
        parse_amount("abc")


def test_parse_invoice_text_extracts_all_fields():
    invoice = parse_invoice_text(SAMPLE_TEXT)
    assert invoice.number == "00000123"
    assert invoice.short_number == "0123"
    assert invoice.client == "Cliente Demo S.A."
    assert invoice.total == Decimal("12345.67")


def test_date_is_read_as_day_month_year():
    invoice = parse_invoice_text(SAMPLE_TEXT)
    assert invoice.issue_date == date(2026, 3, 15)


def test_missing_total_raises_instead_of_returning_zero():
    text = SAMPLE_TEXT.replace("Importe Total: $ 12.345,67", "")
    with pytest.raises(InvoiceParseError) as error:
        parse_invoice_text(text)
    assert "total amount" in str(error.value)


def test_impossible_date_raises():
    text = SAMPLE_TEXT.replace("15/03/2026", "31/02/2026")
    with pytest.raises(InvoiceParseError):
        parse_invoice_text(text)


def test_client_is_not_taken_from_a_longer_number():
    # A 14-digit authorization code must not be mistaken for a tax ID.
    text = "CAE: 74123456789012 vence 22/03/2026\n" + SAMPLE_TEXT
    assert parse_invoice_text(text).client == "Cliente Demo S.A."


def test_extract_folder_reports_unreadable_invoices():
    pytest.importorskip("fitz")  # needs PyMuPDF installed
    invoices, failures = extract_folder(SAMPLES)

    assert len(invoices) == 5
    assert sum(i.total for i in invoices) == Decimal("42730.73")
    assert len(failures) == 1
    assert failures[0].source.name == "factura_0006_incompleta.pdf"
    assert "total amount" in failures[0].reason


def test_extract_folder_missing_folder():
    with pytest.raises(FileNotFoundError):
        extract_folder(SAMPLES / "does-not-exist")
