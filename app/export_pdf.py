from fpdf import FPDF
import tempfile
import os
from datetime import datetime

def sanitize(text: str) -> str:
    """Ensure text is safe for FPDF (no Unicode like ₹)."""
    if not isinstance(text, str):
        text = str(text)
    return text.replace("₹", "Rs.")

def generate_crop_pdf(recommendations, land_area):
    """Generate a PDF report for crop recommendations (Latin-1 safe)."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Use built-in Arial (safe, no external fonts needed)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, sanitize("KrishiMitra AI - Crop Recommendation Report"), 0, 1, "C")
        pdf.ln(5)

        # Add metadata
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, sanitize(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), 0, 1)
        pdf.cell(0, 10, sanitize(f"Land Area: {land_area} acres"), 0, 1)
        pdf.ln(10)

        # Recommendations
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, sanitize("Recommended Crops:"), 0, 1)
        pdf.ln(5)

        for i, crop in enumerate(recommendations, 1):
            pdf.set_font("Arial", "B", 12)
            name = str(crop.get('name', 'Unknown Crop')).title()
            conf = crop.get('confidence')
            conf_txt = f" ({conf*100:.0f}% match)" if conf is not None else ""
            pdf.cell(0, 10, sanitize(f"{i}. {name}{conf_txt}"), 0, 1)

            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, sanitize(f"Expected ROI: Rs. {crop.get('roi', 0):,.2f}"), 0, 1)
            pdf.cell(0, 8, sanitize(f"Profit Potential: Rs. {crop.get('profit', 0):,.2f}"), 0, 1)
            pdf.cell(0, 8, sanitize(f"Investment Needed: Rs. {crop.get('investment', 0):,.2f}"), 0, 1)
            pdf.cell(0, 8, sanitize(f"Market Demand: {crop.get('demand', 'Unknown')}"), 0, 1)
            pdf.cell(0, 8, sanitize(f"Time to Harvest: {crop.get('harvest_time', 'Unknown')} months"), 0, 1)
            pdf.cell(0, 8, sanitize(f"Best Sowing Window: {crop.get('sowing_window', 'Unknown')}"), 0, 1)

            pdf.ln(5)

        # Save PDF to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = temp_file.name
        pdf.output(pdf_path)
        temp_file.close()

        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise Exception("Generated PDF file is empty or doesn't exist")

        return pdf_path

    except Exception as e:
        import traceback
        print("Error generating PDF:", e)
        traceback.print_exc()
        if 'pdf_path' in locals() and os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except:
                pass
        return None
