from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ORANGE = colors.HexColor("#f97316")
MIDGRAY = colors.HexColor("#4b5563")
LIGHTGRAY = colors.HexColor("#e5e7eb")


def fmtdk(value: float) -> str:
    return f"{value:,.2f} kr".replace(",", "X").replace(".", ",").replace("X", ".")


def _draw_footer(c: canvas.Canvas, width: float, y_footer: float, footer_height: float) -> None:
    c.setFillColor(LIGHTGRAY)
    c.rect(0, y_footer, width, footer_height, fill=1, stroke=0)
    c.setFillColor(MIDGRAY)
    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, y_footer + 8 * mm, "Tak for din ordre • kontakt@firma.dk • +45 12 34 56 78")


def _draw_totals(
    c: canvas.Canvas,
    width: float,
    subtotal: float,
    moms_pct: float,
    moms: float,
    total: float,
    y_footer: float,
    footer_height: float,
) -> float:
    totals_height = 26 * mm
    y_tot = y_footer + footer_height + totals_height + 10 * mm

    x_label = 128 * mm
    x_val = width - 20 * mm

    c.setFillColor(MIDGRAY)
    c.setFont("Helvetica", 9)
    c.drawString(x_label, y_tot, "Subtotal")
    c.drawRightString(x_val, y_tot, fmtdk(subtotal))

    c.drawString(x_label, y_tot - 6 * mm, f"MOMS ({moms_pct:.0f}%)")
    c.drawRightString(x_val, y_tot - 6 * mm, fmtdk(moms))

    y_box = y_tot - 16 * mm
    c.setFillColor(ORANGE)
    c.roundRect(x_label - 2 * mm, y_box - 3 * mm, x_val - x_label + 4 * mm, 10 * mm, 2 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_label + 1 * mm, y_box + 1 * mm, "TOTAL DKK")
    c.drawRightString(x_val, y_box + 1 * mm, fmtdk(total))

    return y_tot


def generate_invoice_pdf(filename: str, items: list[dict], moms_pct: float = 25) -> None:
    c = canvas.Canvas(filename, pagesize=A4)
    W, H = A4

    y_footer = 28 * mm
    footer_height = 22 * mm

    top_start = H - 50 * mm
    table_header_y = top_start

    subtotal = sum(item["qty"] * item["price"] for item in items)
    moms = subtotal * moms_pct / 100
    total = subtotal + moms

    def start_page() -> float:
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(MIDGRAY)
        c.drawString(20 * mm, H - 25 * mm, "FAKTURA")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, table_header_y, "Beskrivelse")
        c.drawRightString(150 * mm, table_header_y, "Antal")
        c.drawRightString(175 * mm, table_header_y, "Pris")
        c.drawRightString(W - 20 * mm, table_header_y, "Linjetotal")
        c.setStrokeColor(LIGHTGRAY)
        c.line(20 * mm, table_header_y - 2 * mm, W - 20 * mm, table_header_y - 2 * mm)
        return table_header_y - 10 * mm

    y_row = start_page()
    y_tot = _draw_totals(c, W, subtotal, moms_pct, moms, total, y_footer, footer_height)

    min_gap = 10 * mm
    for item in items:
        if y_row <= y_tot + min_gap:
            c.showPage()
            y_row = start_page()
            y_tot = _draw_totals(c, W, subtotal, moms_pct, moms, total, y_footer, footer_height)

        line_total = item["qty"] * item["price"]
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(20 * mm, y_row, item["name"])
        c.drawRightString(150 * mm, y_row, str(item["qty"]))
        c.drawRightString(175 * mm, y_row, fmtdk(item["price"]))
        c.drawRightString(W - 20 * mm, y_row, fmtdk(line_total))
        y_row -= 8 * mm

    _draw_footer(c, W, y_footer, footer_height)
    c.save()


if __name__ == "__main__":
    sample_items = [
        {"name": "Udviklingstimer", "qty": 2, "price": 950.0},
        {"name": "Design", "qty": 1, "price": 700.0},
    ]
    generate_invoice_pdf("invoice.pdf", sample_items)
