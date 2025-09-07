from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_PDF = BASE_DIR / 'Technical_Approach.pdf'

def generate_technical_approach_pdf():
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=letter)
    width, height = letter

    lines = [
        "Medical Appointment Scheduling AI Agent - Technical Approach",
        "",
        "Architecture: LangChain + LangGraph orchestrate agents (Greeting, Lookup, Scheduling,",
        "Insurance, Confirmation, Reminders). Streamlit provides chat UI and admin panel.",
        "",
        "Framework Choice: LangGraph for deterministic stateful flows; LangChain for LLM IO",
        "abstractions and message management.",
        "",
        "Integration: pandas + openpyxl read/write patients.csv and doctor_schedule.xlsx;",
        "python-docx provides intake form attachment; smtplib/Twilio simulated via console.",
        "",
        "Challenges: Disambiguating user info -> solved with clear prompts and heuristics;",
        "slot selection -> earliest available filtered by doctor/location/type;",
        "robustness -> validations and friendly fallbacks.",
    ]

    y = height - 72
    for line in lines:
        c.drawString(72, y, line)
        y -= 16

    c.showPage()
    c.save()

if __name__ == '__main__':
    generate_technical_approach_pdf()
