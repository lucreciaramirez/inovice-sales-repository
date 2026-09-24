"""Generate FAKE sample invoices in ``samples/`` so the tool can be tried without real data.

Every name, tax ID and amount below is invented.

Usage (from the project root):
    pip install -r requirements-dev.txt
    python scripts/generate_sample_invoices.py
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "samples"

# (invoice number, date, fake tax ID, client, total as printed) - total None = incomplete invoice
INVOICES = [
    ("00000001", "15/03/2026", "30000000019", "Cliente Demo S.A.", "12.345,67"),
    ("00000002", "18/03/2026", "30000000027", "Ferretería Ejemplo S.R.L.", "5.400,00"),
    ("00000003", "02/04/2026", "30000000019", "Cliente Demo S.A.", "8.750,50"),
    ("00000004", "20/12/2025", "30000000035", "Kiosco Modelo", "1.234,56"),
    ("00000005", "09/01/2026", "30000000027", "Ferretería Ejemplo S.R.L.", "15.000,00"),
    ("00000006", "21/04/2026", "30000000035", "Kiosco Modelo", None),  # deliberately incomplete
]


def draw_invoice(path: Path, number: str, issue_date: str, tax_id: str, client: str, total):
    c = canvas.Canvas(str(path), pagesize=A4)
    _, height = A4
    lines = [
        "FACTURA C (MUESTRA - DATOS FICTICIOS)",
        f"Comp. Nro: 00003 {number}",
        f"Fecha de Emisión: {issue_date}",
        "Emisor: Comercio Demo",
        "Datos del cliente",
        tax_id,
        client,
        "Concepto: Venta de mercaderías (ejemplo)",
    ]
    if total is not None:
        lines.append(f"Importe Total: $ {total}")

    y = height - 80
    for line in lines:
        c.drawString(60, y, line)
        y -= 22
    c.save()


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for number, issue_date, tax_id, client, total in INVOICES:
        name = f"factura_{number[-4:]}.pdf" if total else f"factura_{number[-4:]}_incompleta.pdf"
        draw_invoice(OUTPUT_DIR / name, number, issue_date, tax_id, client, total)
        print("created", name)


if __name__ == "__main__":
    main()
