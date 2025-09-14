from fpdf import FPDF
import tempfile
import os
import textwrap

class CropReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Use built-in Arial font (supports basic Unicode)
        self.set_font('Arial', '', 12)

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
    pdf = CropReportPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="KrishiMitra AI - Crop Recommendations", ln=True, align='C')
    pdf.ln(5)
    
    # Date and land area
    from datetime import datetime
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(0, 8, f"Land Area: {land_area} acres", ln=True)
    pdf.ln(5)

    for idx, crop in enumerate(recommendations, 1):
        # Crop name
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, clean_text(f"{idx}. {crop['name'].title()}"), ln=True)
        
        # Financial information
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, clean_text(f"Expected ROI: Rs.{crop['roi']:,.0f}"), ln=True)
        pdf.cell(0, 6, clean_text(f"Profit Potential: Rs.{crop['profit']:,.0f}"), ln=True)
        pdf.cell(0, 6, clean_text(f"Investment Required: Rs.{crop['investment']:,.0f}"), ln=True)
        
        # Timing information
        pdf.cell(0, 6, clean_text(f"Harvest Time: {crop['harvest_time']} months"), ln=True)
        pdf.cell(0, 6, clean_text(f"Sowing Window: {crop['sowing_window']}"), ln=True)
        pdf.cell(0, 6, clean_text(f"Market Demand: {crop['demand']}"), ln=True)
        
        # Tips and warnings
        tips = clean_text(', '.join(crop.get('tips', [])))
        warnings = clean_text(', '.join(crop.get('warnings', [])))
        
        if tips:
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "Best Practices:", ln=True)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(190, 5, wrap_text(f"- {tips}", width=85))
        
        if warnings:
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "Important Warnings:", ln=True)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(190, 5, wrap_text(f"- {warnings}", width=85))
        
        pdf.ln(8)  # Space between crops

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name
