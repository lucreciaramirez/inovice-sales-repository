# Invoice Sales Summary

A small desktop tool that reads a folder of PDF invoices, extracts the key data from each one, and produces an Excel report with the sales detail and totals per client.

I built it to replace a manual task: adding up my family business's monthly sales from their invoices. What used to be copying numbers by hand is now one click.

## What it does

1. You pick a folder with invoices in PDF format.
2. For every PDF it extracts the **invoice number, issue date, client name and total amount**.
3. It writes `resumen_facturas.xlsx` in that folder, with:
   - **Detalle**: one row per invoice, ordered by date
   - **Resumen por cliente**: number of invoices and total sales per client, plus a grand total
   - **No procesadas** (only if needed): the files it could not read and why, so nothing is silently left out

## Try it in two minutes (with fake data)

The `samples/` folder contains invented invoices. No real data is included in this repository.

```bash
git clone https://github.com/<your-username>/invoice-sales-summary.git
cd invoice-sales-summary
python -m venv .venv
.venv\Scripts\activate          # Windows  (on Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt

python -m invoice_summary --folder samples
```

Result for the sample folder (5 readable invoices, 1 deliberately incomplete):

| Razón Social | Cantidad de facturas | Importe Total |
|---|---|---|
| Cliente Demo S.A. | 2 | 21,096.17 |
| Ferretería Ejemplo S.R.L. | 2 | 20,400.00 |
| Kiosco Modelo | 1 | 1,234.56 |
| **TOTAL GENERAL** | **5** | **42,730.73** |

The incomplete invoice appears in the **No procesadas** sheet with the reason (`Missing: total amount`) instead of being counted as zero.

## Usage

**With the window** (the way it is meant to be used day to day):

```bash
python -m invoice_summary
```

Click **Procesar Facturas**, choose the folder with your PDFs, and the Excel file is created next to them.

**Without a window** (handy for scripts or testing):

```bash
python -m invoice_summary --folder path/to/invoices
```

## Adapting it to your invoices

The invoice fields are found with regular expressions defined at the top of [`invoice_summary/extractor.py`](invoice_summary/extractor.py):

```python
INVOICE_NUMBER_RE = re.compile(r"Comp\. Nro:\s*\d+\s+(\d+)")
ISSUE_DATE_RE = re.compile(r"Fecha de Emisión:\s*(\d{2})/(\d{2})/(\d{4})")  # dd/mm/yyyy
CLIENT_RE = re.compile(r"\b\d{11}\b\s+(.+)")
TOTAL_RE = re.compile(r"Importe Total:\s*\$\s*([\d.,]+)")
```

They are written for the layout of the invoices this tool was made for (Argentine electronic invoices: dates as `dd/mm/yyyy`, amounts as `1.234,56`, client name right after the client's 11-digit tax ID). If your invoices are laid out differently, these are the only lines you should need to change.

## Design decisions

- **Errors are reported, not hidden.** A file that can't be read, or an invoice missing a field, goes to the *No procesadas* sheet. A missing total is never counted as `0`.
- **Money is handled with `Decimal`**, not floating point, so the totals add up to the cent.
- **Parsing is separated from PDF reading and from the interface**, so the extraction logic can be tested without opening a PDF or a window.
- **Full dates are kept** (day, month and year), so invoices from different years are never mixed up.

## Project structure

```
invoice_summary/
  extractor.py   # PDF -> text -> Invoice (regular expressions, validation)
  report.py      # invoices -> pandas tables -> formatted Excel file
  pipeline.py    # the whole process in one function
  gui.py         # tkinter window
  __main__.py    # entry point (window or --folder)
samples/         # fake invoices for trying the tool
scripts/         # generator for the fake invoices
tests/           # pytest tests
```

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Privacy

Real invoices contain names, tax IDs and amounts. The `.gitignore` in this repository excludes every PDF (except the fake ones in `samples/`) and every Excel file, so real data is not committed by accident. Before pushing your own changes, run `git status` and check that only code files are listed.

## Ideas for the future

- Read invoices that are scanned images (OCR)
- Filter the report by date range or month
- Support other invoice layouts through a configuration file
- Package it as a Windows `.exe`

## License

[MIT](LICENSE). Built by Lucrecia Ramírez.
