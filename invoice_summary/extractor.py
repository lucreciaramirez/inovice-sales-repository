"""Read electronic invoices (PDF) and extract the data needed for a sales summary.

The reading is split in two steps so each one is easy to test:

1. ``read_pdf_text``   -> PDF file to plain text (uses PyMuPDF)
2. ``parse_invoice_text`` -> plain text to an ``Invoice`` (pure Python, regular expressions)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------
# These match the invoice layout this tool was written for. If your invoices
# look different, these four lines are the only ones you should need to adapt.
INVOICE_NUMBER_RE = re.compile(r"Comp\. Nro:\s*\d+\s+(\d+)")
ISSUE_DATE_RE = re.compile(r"Fecha de Emisión:\s*(\d{2})/(\d{2})/(\d{4})")  # dd/mm/yyyy
# Text that follows the first 11-digit tax ID (CUIT). \b avoids matching a piece
# of a longer number, such as a 14-digit authorization code.
CLIENT_RE = re.compile(r"\b\d{11}\b\s+(.+)")
TOTAL_RE = re.compile(r"Importe Total:\s*\$\s*([\d.,]+)")


class InvoiceParseError(Exception):
    """Raised when an invoice does not contain the expected data."""


@dataclass(frozen=True)
class Invoice:
    number: str
    issue_date: date
    client: str
    total: Decimal
    source: Path

    @property
    def short_number(self) -> str:
        """Last four digits of the invoice number, as shown in the report."""
        return self.number[-4:]


@dataclass(frozen=True)
class ParseFailure:
    source: Path
    reason: str


def parse_amount(raw: str) -> Decimal:
    """Convert an amount written in Argentine format ('1.234,56') to a Decimal."""
    cleaned = raw.strip().rstrip(".,").replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount: {raw!r}") from exc


def parse_invoice_text(text: str, source: Path | str = Path("<text>")) -> Invoice:
    """Extract the invoice data from its text.

    Raises ``InvoiceParseError`` listing every field that could not be found,
    instead of silently returning empty values or zeros.
    """
    source = Path(source)
    number_match = INVOICE_NUMBER_RE.search(text)
    date_match = ISSUE_DATE_RE.search(text)
    client_match = CLIENT_RE.search(text)
    total_match = TOTAL_RE.search(text)

    missing = [
        label
        for label, match in (
            ("invoice number", number_match),
            ("issue date", date_match),
            ("client", client_match),
            ("total amount", total_match),
        )
        if match is None
    ]
    if missing:
        raise InvoiceParseError("Missing: " + ", ".join(missing))

    day, month, year = (int(g) for g in date_match.groups())
    try:
        issue_date = date(year, month, day)
    except ValueError as exc:
        raise InvoiceParseError(f"Invalid issue date: {day:02d}/{month:02d}/{year}") from exc

    try:
        total = parse_amount(total_match.group(1))
    except ValueError as exc:
        raise InvoiceParseError(str(exc)) from exc

    return Invoice(
        number=number_match.group(1),
        issue_date=issue_date,
        client=client_match.group(1).strip(),
        total=total,
        source=source,
    )


def read_pdf_text(pdf_path: Path | str) -> str:
    """Return all the text of a PDF."""
    import fitz  # PyMuPDF. Imported here so the parsing logic works without it.

    with fitz.open(str(pdf_path)) as doc:
        return "".join(page.get_text() for page in doc)


def extract_invoice(pdf_path: Path | str) -> Invoice:
    pdf_path = Path(pdf_path)
    return parse_invoice_text(read_pdf_text(pdf_path), pdf_path)


def extract_folder(folder: Path | str) -> tuple[list[Invoice], list[ParseFailure]]:
    """Process every PDF in a folder.

    Returns the invoices that could be read and, separately, the files that
    could not (with the reason), so nothing is lost without notice.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    invoices: list[Invoice] = []
    failures: list[ParseFailure] = []
    for pdf in sorted(p for p in folder.iterdir() if p.suffix.lower() == ".pdf"):
        try:
            invoice = extract_invoice(pdf)
        except InvoiceParseError as exc:
            failures.append(ParseFailure(pdf, str(exc)))
            logger.warning("Skipped %s: %s", pdf.name, exc)
        except Exception as exc:  # corrupt or unreadable PDF, etc.
            failures.append(ParseFailure(pdf, f"Could not read file: {exc}"))
            logger.warning("Could not read %s: %s", pdf.name, exc)
        else:
            invoices.append(invoice)
            logger.info("Processed %s (invoice %s)", pdf.name, invoice.short_number)
    return invoices, failures
