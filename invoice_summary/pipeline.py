"""The whole process in one function, shared by the window and the command line."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from .extractor import ParseFailure, extract_folder
from .report import export_excel

OUTPUT_NAME = "resumen_facturas.xlsx"


class NoInvoicesError(Exception):
    """No invoice could be read from the folder."""


@dataclass(frozen=True)
class RunResult:
    output_path: Path
    processed: int
    failures: list[ParseFailure]
    grand_total: Decimal


def process_folder(folder: Path | str) -> RunResult:
    folder = Path(folder)
    invoices, failures = extract_folder(folder)
    if not invoices:
        if failures:
            raise NoInvoicesError(
                f"No data could be extracted from the {len(failures)} PDF file(s) found."
            )
        raise NoInvoicesError("No PDF files found in the selected folder.")

    output_path = export_excel(invoices, failures, folder / OUTPUT_NAME)
    return RunResult(
        output_path=output_path,
        processed=len(invoices),
        failures=failures,
        grand_total=sum((i.total for i in invoices), Decimal("0")),
    )
