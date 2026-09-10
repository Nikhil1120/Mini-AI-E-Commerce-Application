"""Generate PDF versions of submission text files."""
from fpdf import FPDF
from pathlib import Path


def txt_to_pdf(txt_path: Path, pdf_path: Path) -> None:
    text = txt_path.read_text(encoding="utf-8")
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Courier", size=7)

    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    for line in text.splitlines():
        # Replace unsupported Unicode with ASCII equivalents
        line = (
            line.replace("—", "-")
            .replace("–", "-")
            .replace("→", "->")
            .replace("←", "<-")
            .replace("↔", "<->")
            .replace("•", "-")
            .replace("…", "...")
        )
        safe = line.encode("latin-1", "replace").decode("latin-1")

        if not safe:
            pdf.ln(3)
            continue

        pdf.multi_cell(page_width, 3.2, safe)

    pdf.output(str(pdf_path))
    print(f"Created: {pdf_path}")


if __name__ == "__main__":
    base = Path(__file__).parent
    for name in (
        "ONE_PAGE_SYSTEM_DESIGN",
        "SUBMISSION",
        "README",
        "DATABASE_SCHEMA",
        "API_DOCUMENTATION",
    ):
        txt_to_pdf(base / f"{name}.txt", base / f"{name}.pdf")
