from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd
from email.message import EmailMessage

BASE_DIR = Path(__file__).resolve().parents[2]
PATIENTS_CSV = BASE_DIR / 'patients.csv'
DOCTOR_XLSX = BASE_DIR / 'doctor_schedule.xlsx'
APPT_EXPORT_XLSX = BASE_DIR / 'appointments_export.xlsx'
INTAKE_FORM = BASE_DIR / 'appointment_forms' / 'New Patient Intake Form.docx'


def load_patients() -> pd.DataFrame:
    if not PATIENTS_CSV.exists():
        raise FileNotFoundError(f"Missing patients.csv at {PATIENTS_CSV}")
    df = pd.read_csv(PATIENTS_CSV)
    return df


def load_schedule() -> pd.DataFrame:
    if not DOCTOR_XLSX.exists():
        raise FileNotFoundError(f"Missing doctor_schedule.xlsx at {DOCTOR_XLSX}")
    df = pd.read_excel(DOCTOR_XLSX, sheet_name='schedule')
    return df


def save_schedule(df: pd.DataFrame) -> None:
    # Preserve doctors sheet if present
    doctors_df: Optional[pd.DataFrame] = None
    if DOCTOR_XLSX.exists():
        try:
            doctors_df = pd.read_excel(DOCTOR_XLSX, sheet_name='doctors')
        except Exception:
            doctors_df = None
    with pd.ExcelWriter(DOCTOR_XLSX, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='schedule', index=False)
        if doctors_df is not None:
            doctors_df.to_excel(writer, sheet_name='doctors', index=False)


def append_appointment_export(rows: List[Dict[str, Any]]) -> None:
    if APPT_EXPORT_XLSX.exists():
        existing = pd.read_excel(APPT_EXPORT_XLSX, sheet_name='appointments')
        new_df = pd.concat([existing, pd.DataFrame(rows)], ignore_index=True)
    else:
        new_df = pd.DataFrame(rows)
    with pd.ExcelWriter(APPT_EXPORT_XLSX, engine='openpyxl') as writer:
        new_df.to_excel(writer, sheet_name='appointments', index=False)


def simulate_send_email(to: str, subject: str, body: str, attachments: Optional[List[Path]] = None) -> None:
    msg = EmailMessage()
    msg['To'] = to
    msg['From'] = 'no-reply@clinic.example'
    msg['Subject'] = subject
    msg.set_content(body)
    print("=== Simulated Email ===")
    print(msg)
    if attachments:
        for path in attachments:
            print(f"Attachment: {path}")
    print("=======================")


def simulate_send_sms(to: str, body: str) -> None:
    print("=== Simulated SMS ===")
    print(f"To: {to}\nBody: {body}")
    print("====================")
