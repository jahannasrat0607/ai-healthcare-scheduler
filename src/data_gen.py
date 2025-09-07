import random
import string
from datetime import date, timedelta, datetime
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PATIENTS_CSV = BASE_DIR / 'patients.csv'
DOCTOR_XLSX = BASE_DIR / 'doctor_schedule.xlsx'

FIRST_NAMES = [
    'Aarav','Vivaan','Ishaan','Diya','Priya','Rohan','Ananya','Kunal','Neha','Rahul',
    'Saanvi','Aditi','Arjun','Meera','Ritika',
    'Ayaan','Zara','Imran','Fatima','Aisha','Rehan','Sana','Yusuf','Zoya','Nadia',
    'Joseph','Mary','John','Thomas','Elizabeth','Peter','Paul','Annie','Rita','Daniel'
]
LAST_NAMES = [
    'Sharma','Gupta','Iyer','Nair','Reddy','Patel','Mehta','Joshi','Kapoor','Singh',
    'Khan','Ali','Ahmed','Sheikh','Ansari','Qureshi','Hussain','Syed',
    "D'Souza","Fernandes","Thomas","Joseph","Rodrigues","Pereira","Lobo"
]
STREETS = ['MG Road','Link Road','Park Street','Church Street','Station Road','Temple Road','Lake View']
CITIES = ['Mumbai','Delhi','Bengaluru','Hyderabad','Chennai']
STATES = ['MH','DL','KA','TS','TN']
INSURERS = ['Blue Cross','Aetna','UnitedHealth','Cigna','Star Health']

DOCTORS = [
    {'doctor_id': 'D100', 'name': 'Dr. Arjun Sharma', 'location': 'Mumbai Central'},
    {'doctor_id': 'D200', 'name': 'Dr. Sana Khan', 'location': 'Delhi Connaught Place'},
    {'doctor_id': 'D300', 'name': "Dr. Maria D'Souza", 'location': 'Bengaluru Indiranagar'},
]


def random_phone() -> str:
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def random_email(first: str, last: str) -> str:
    domain = random.choice(['gmail.com','yahoo.com','outlook.com','example.com'])
    return f"{first.lower()}.{last.lower()}{random.randint(1,99)}@{domain}"


def random_dob(min_age=18, max_age=90) -> date:
    today = date.today()
    age = random.randint(min_age, max_age)
    days_offset = random.randint(0, 365)
    return today.replace(year=today.year - age) - timedelta(days=days_offset)


def random_member_id() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def random_group_number() -> str:
    return ''.join(random.choices(string.digits, k=6))


def generate_patients(n: int = 50) -> pd.DataFrame:
    rows = []
    for i in range(n):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        row = {
            'patient_id': f"P{1000+i}",
            'first_name': first,
            'last_name': last,
            'dob': random_dob().isoformat(),
            'gender': random.choice(['Male','Female','Other']),
            'phone': random_phone(),
            'email': random_email(first, last),
            'address': f"{random.randint(100,9999)} {random.choice(STREETS)}",
            'city': random.choice(CITIES),
            'state': random.choice(STATES),
            'zip': f"{random.randint(10000,99999)}",
            'emergency_contact_name': f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            'emergency_contact_phone': random_phone(),
            'insurance_carrier': random.choice(INSURERS),
            'insurance_member_id': random_member_id(),
            'insurance_group_number': random_group_number(),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def generate_doctor_schedule() -> pd.DataFrame:
    # Create slots for Mon-Fri next two weeks, 09:00-17:00
    start_date = date.today() + timedelta(days=(7 - date.today().weekday()) % 7)  # next Monday or today if Monday
    days = [start_date + timedelta(days=d) for d in range(0, 14) if (start_date + timedelta(days=d)).weekday() < 5]
    slots = []
    for doc in DOCTORS:
        for d in days:
            start_time = datetime(d.year, d.month, d.day, 9, 0)
            end_time = datetime(d.year, d.month, d.day, 17, 0)
            t = start_time
            while t < end_time:
                duration = 60 if (t.hour == 9) else 30  # First slot 60min for new patients, rest 30min
                slots.append({
                    'doctor_id': doc['doctor_id'],
                    'doctor_name': doc['name'],
                    'location': doc['location'],
                    'date': t.date().isoformat(),
                    'start_time': t.strftime('%H:%M'),
                    'end_time': (t + timedelta(minutes=duration)).strftime('%H:%M'),
                    'slot_type': 'new' if duration == 60 else 'returning',
                    'available': True,
                    'appointment_id': '',
                    'patient_id': '',
                })
                t += timedelta(minutes=duration)
    return pd.DataFrame(slots)


def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    patients = generate_patients(50)
    patients.to_csv(PATIENTS_CSV, index=False)

    schedule = generate_doctor_schedule()
    with pd.ExcelWriter(DOCTOR_XLSX, engine='openpyxl') as writer:
        schedule.to_excel(writer, sheet_name='schedule', index=False)
        pd.DataFrame(DOCTORS).to_excel(writer, sheet_name='doctors', index=False)

    print(f"Wrote {PATIENTS_CSV}")
    print(f"Wrote {DOCTOR_XLSX}")


if __name__ == '__main__':
    main()
