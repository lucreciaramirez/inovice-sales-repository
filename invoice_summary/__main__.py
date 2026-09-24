"""Entry point: ``python -m invoice_summary`` (window) or with ``--folder`` (no window)."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .pipeline import NoInvoicesError, process_folder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="invoice_summary",
        description="Summarize a folder of PDF invoices into an Excel report.",
    )
    parser.add_argument(
        "--folder",
        type=Path,
        help="Process this folder directly, without opening the window.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.folder is None:
        from .gui import launch  # imported here so --folder works without tkinter

        launch()
        return 0

    try:
        result = process_folder(args.folder)
    except (NoInvoicesError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"\nInvoices processed: {result.processed}")
    print(f"Grand total: $ {result.grand_total:,.2f}")
    print(f"Report saved to: {result.output_path}")
    if result.failures:
        print(f"Files that could not be read: {len(result.failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
