from fpdf import FPDF
import tempfile
import os
import textwrap

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansDevanagari-Regular.ttf")

class HindiPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('NotoSansDevanagari', '', FONT_PATH, uni=True)
        self.set_font('NotoSansDevanagari', '', 12)

def clean_text(text):
    if not isinstance(text, str):
        text = str(text)
    return (
        text.replace("₹", "Rs.")
            .replace("–", "-")
            .replace("—", "-")
            .replace("’", "'")
            .replace("‘", "'")
            .replace("“", '"')
            .replace("”", '"')
            .replace(",", ", ")  # helps splitting long lines
            .replace("•", "-")
    )

def wrap_text(text, width=100):
    """Wrap long strings to avoid FPDF crashing on wide words."""
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=True))

def generate_crop_pdf(recommendations, land_area):
    pdf = HindiPDF()
    pdf.add_page()
    pdf.set_font("NotoSansDevanagari", '', 14)
    pdf.cell(200, 10, txt="KrishiMitraAI - फसल सिफारिशें", ln=True, align='C')
    pdf.ln(10)

    for idx, crop in enumerate(recommendations, 1):
        pdf.set_font("NotoSansDevanagari", '', 12)
        pdf.cell(0, 10, clean_text(f"{idx}. {crop['name']}"), ln=True)
        pdf.cell(0, 10, clean_text(f"ROI: Rs.{crop['roi']:,.0f} | Profit: Rs.{crop['profit']:,.0f} | Investment: Rs.{crop['investment']:,.0f}"), ln=True)
        pdf.cell(0, 10, clean_text(f"Harvest: {crop['harvest_time']} months | Sowing: {crop['sowing_window']} | Demand: {crop['demand']}"), ln=True)

        tips = clean_text(', '.join(crop.get('tips', [])))
        warnings = clean_text(', '.join(crop.get('warnings', [])))

        pdf.multi_cell(190, 10, wrap_text(f"Tips: {tips}", width=90))
        pdf.multi_cell(190, 10, wrap_text(f"Warnings: {warnings}", width=90))
        pdf.ln(5)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name
