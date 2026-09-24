"""Small desktop window: pick a folder, get the Excel report."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from .pipeline import NoInvoicesError, process_folder


def _on_process() -> None:
    folder = filedialog.askdirectory(title="Elegí la carpeta con las facturas (PDF)")
    if not folder:
        return
    try:
        result = process_folder(folder)
    except NoInvoicesError as exc:
        messagebox.showerror("Error", str(exc))
        return
    except Exception as exc:
        messagebox.showerror("Error inesperado", str(exc))
        return

    message = (
        f"Facturas procesadas: {result.processed}\n"
        f"Total general: $ {result.grand_total:,.2f}\n\n"
        f"Resumen guardado en:\n{result.output_path}"
    )
    if result.failures:
        names = "\n".join(f"- {f.source.name}: {f.reason}" for f in result.failures[:5])
        extra = len(result.failures) - 5
        if extra > 0:
            names += f"\n... y {extra} más"
        message += f"\n\nNo se pudieron leer {len(result.failures)} archivo(s):\n{names}"
        messagebox.showwarning("Listo, con avisos", message)
    else:
        messagebox.showinfo("Éxito", message)


def launch() -> None:
    window = tk.Tk()
    window.title("Resumen De Ventas")
    window.geometry("400x200")

    tk.Label(
        window,
        text="Elegí la carpeta con las facturas en PDF\ny generá el resumen en Excel",
        font=("Arial", 12),
    ).pack(pady=20)
    tk.Button(
        window,
        text="Procesar Facturas",
        command=_on_process,
        font=("Arial", 12),
        bg="#E5C1F9",
        fg="black",
    ).pack(pady=10)

    window.mainloop()
