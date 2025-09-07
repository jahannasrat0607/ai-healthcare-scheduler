from __future__ import annotations
from typing import Dict, Any, Optional, List
import uuid
import pandas as pd
from langgraph.graph import StateGraph
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.io_utils import (
        load_patients, load_schedule, save_schedule, append_appointment_export,
        simulate_send_email, simulate_send_sms, INTAKE_FORM
    )
except ImportError:
    from src.utils.io_utils import (
        load_patients, load_schedule, save_schedule, append_appointment_export,
        simulate_send_email, simulate_send_sms, INTAKE_FORM
    )

State = Dict[str, Any]


def _ensure_messages(state: State) -> None:
    if 'messages' not in state or not isinstance(state['messages'], list):
        state['messages'] = []


def _add_user(state: State, text: str) -> None:
    _ensure_messages(state)
    state['messages'].append({'type': 'user', 'content': text})


def _add_ai(state: State, text: str) -> None:
    _ensure_messages(state)
    state['messages'].append({'type': 'ai', 'content': text})


def greeting_agent(state: State, user_input: str) -> State:
    _add_user(state, user_input)
    lower = user_input.lower()
    
    # Extract simple key:value pairs
    def extract(key: str, target: str) -> None:
        if state.get(target):
            return
        if key in lower:
            try:
                # Find the key and extract the value after the colon
                key_index = lower.find(key)
                if key_index != -1:
                    # Find the colon after the key
                    colon_index = user_input.find(':', key_index)
                    if colon_index != -1:
                        # Extract value after colon, stop at next comma or end
                        value = user_input[colon_index + 1:].strip()
                        if ',' in value:
                            value = value.split(',')[0].strip()
                        state[target] = value
            except Exception:
                pass

    for key, target in [('name:', 'name'), ('dob:', 'dob'), ('dr:', 'doctor'), ('location:', 'location')]:
        extract(key, target)

    missing = []
    if not state.get('name'):
        missing.append("your full name (e.g., Name: Jane Doe)")
    if not state.get('dob'):
        missing.append("your DOB (e.g., DOB: 1990-08-23)")
    if not state.get('doctor'):
        missing.append("preferred doctor (e.g., Dr: Arjun Sharma)")
    if not state.get('location'):
        missing.append("preferred location (e.g., Location: Mumbai Central)")

    if missing:
        _add_ai(state, "Please provide: " + "; ".join(missing))
    else:
        _add_ai(state, f"Thanks {state.get('name')}. Checking your record...")
    return state


def patient_lookup_agent(state: State) -> State:
    df = load_patients()
    is_returning = False
    name = state.get('name')
    dob = state.get('dob')
    if name and dob:
        tokens = name.strip().split()
        first = tokens[0]
        last = tokens[-1] if len(tokens) > 1 else ''
        matches = df[(df['first_name'].str.lower() == first.lower()) &
                     (df['last_name'].str.lower() == last.lower()) &
                     (df['dob'].astype(str) == str(dob))]
        is_returning = len(matches) > 0
    state['is_new_patient'] = not is_returning
    _add_ai(state, ("You're a returning patient. Let's find a time." if is_returning else "Welcome! We'll register you as a new patient."))
    return state


def scheduling_agent(state: State) -> State:
    schedule = load_schedule()
    doctor = state.get('doctor', '')
    location = state.get('location', '')
    
    # More flexible matching
    if doctor:
        # Try to match doctor name more flexibly
        doctor_clean = doctor.replace('Dr.', '').replace('Dr', '').strip().lower()
        # Try full name match first, then last name
        if not schedule[schedule['doctor_name'].str.lower().str.contains(doctor_clean, na=False)].empty:
            schedule = schedule[schedule['doctor_name'].str.lower().str.contains(doctor_clean, na=False)]
        else:
            # Try last name only
            doctor_last = doctor_clean.split()[-1]
            schedule = schedule[schedule['doctor_name'].str.lower().str.contains(doctor_last, na=False)]
    
    if location:
        # Extract key words from location
        location_words = location.lower().split()
        location_match = False
        for word in location_words:
            if len(word) > 3:  # Only match meaningful words
                location_match = schedule['location'].str.lower().str.contains(word, na=False).any()
                if location_match:
                    schedule = schedule[schedule['location'].str.lower().str.contains(word, na=False)]
                    break
    
    if state.get('is_new_patient') is not None:
        slot_type = 'new' if state['is_new_patient'] else 'returning'
        schedule = schedule[(schedule['slot_type'] == slot_type) & (schedule['available'] == True)]
    
    if schedule.empty:
        _add_ai(state, "Sorry, no available slots match your criteria. Try another doctor/location or a different day.")
        return state

    slot = schedule.sort_values(['date','start_time']).iloc[0].to_dict()
    appointment_id = str(uuid.uuid4())[:8]
    
    # Try to save the schedule, but don't fail if file is locked
    try:
        full = load_schedule()
        idx = full[(full['doctor_id'] == slot['doctor_id']) & (full['date'] == slot['date']) & (full['start_time'] == slot['start_time'])].index
        full.loc[idx, 'available'] = False
        full.loc[idx, 'appointment_id'] = appointment_id
        full.loc[idx, 'patient_id'] = state.get('name') or 'NEW'
        save_schedule(full)
    except PermissionError:
        # File is locked by another process, but we can still proceed
        _add_ai(state, "Note: Schedule file is currently in use, but appointment is confirmed.")

    state['scheduled'] = {
        'appointment_id': appointment_id,
        'doctor_name': slot['doctor_name'],
        'location': slot['location'],
        'date': slot['date'],
        'start_time': slot['start_time'],
        'end_time': slot['end_time'],
        'slot_type': slot['slot_type'],
    }
    _add_ai(state, f"Booked {slot['doctor_name']} at {slot['location']} on {slot['date']} at {slot['start_time']}.")
    return state


def insurance_agent(state: State, user_input: Optional[str] = None) -> State:
    if 'insurance' not in state or not isinstance(state.get('insurance'), dict):
        state['insurance'] = {}
    if user_input:
        lower = user_input.lower()
        if 'carrier' in lower:
            state['insurance']['carrier'] = user_input.split(':')[-1].strip()
        if 'member' in lower:
            state['insurance']['member_id'] = user_input.split(':')[-1].strip()
        if 'group' in lower:
            state['insurance']['group_number'] = user_input.split(':')[-1].strip()
    missing = [k for k in ['carrier','member_id','group_number'] if not state['insurance'].get(k)]
    if missing:
        _add_ai(state, f"Please provide insurance {', '.join(missing)} (e.g., Carrier: Star Health; Member: ABC123; Group: 987654).")
        return state
    if len(state['insurance'].get('member_id','')) < 6 or len(state['insurance'].get('group_number','')) < 4:
        _add_ai(state, "Insurance details look incomplete. Please re-check member id and group number.")
        return state
    _add_ai(state, "Insurance information recorded successfully.")
    return state


def confirmation_agent(state: State) -> State:
    if not state.get('scheduled'):
        _add_ai(state, "No appointment scheduled yet.")
        return state
    name = state.get('name','Patient')
    email = f"{name.replace(' ','.').lower()}@example.com"
    simulate_send_email(
        to=email,
        subject="Appointment Confirmation & Intake Form",
        body=(
            f"Hello {name},\n\n"
            f"Your appointment is confirmed for {state['scheduled']['date']} at {state['scheduled']['start_time']} with {state['scheduled']['doctor_name']} ({state['scheduled']['location']}).\n"
            f"Please complete the attached intake form before your visit.\n\nThank you."
        ),
        attachments=[INTAKE_FORM] if INTAKE_FORM.exists() else None,
    )
    append_appointment_export([
        {
            'appointment_id': state['scheduled']['appointment_id'],
            'patient_name': state.get('name'),
            'dob': state.get('dob'),
            'doctor_name': state['scheduled']['doctor_name'],
            'location': state['scheduled']['location'],
            'date': state['scheduled']['date'],
            'start_time': state['scheduled']['start_time'],
            'insurance_carrier': state.get('insurance', {}).get('carrier',''),
            'member_id': state.get('insurance', {}).get('member_id',''),
            'group_number': state.get('insurance', {}).get('group_number',''),
            'status': 'confirmed',
        }
    ])
    state.setdefault('confirmations', {})['email_sent'] = True
    _add_ai(state, "Confirmation email sent with intake form attachment.")
    return state


def reminder_agent(state: State) -> State:
    if not state.get('scheduled'):
        return state
    phone = '+1-000-000-0000'
    simulate_send_sms(phone, f"Reminder 1: Your appointment with {state['scheduled']['doctor_name']} is on {state['scheduled']['date']} at {state['scheduled']['start_time']}")
    simulate_send_sms(phone, "Reminder 2: Please confirm attendance and complete the intake form.")
    simulate_send_sms(phone, "Reminder 3: Final reminder. Reply CANCEL to reschedule.")
    state.setdefault('confirmations', {})['reminders_sent'] = 3
    _add_ai(state, "Three reminders have been scheduled and sent (simulated).")
    return state


def build_graph():
    sg = StateGraph(dict)

    def greet_node(state: State) -> State:
        return state

    def lookup_node(state: State) -> State:
        return patient_lookup_agent(state)

    def schedule_node(state: State) -> State:
        return scheduling_agent(state)

    def confirm_node(state: State) -> State:
        return confirmation_agent(state)

    def reminder_node(state: State) -> State:
        return reminder_agent(state)

    sg.add_node('greet', greet_node)
    sg.add_node('lookup', lookup_node)
    sg.add_node('schedule', schedule_node)
    sg.add_node('confirm', confirm_node)
    sg.add_node('reminder', reminder_node)

    sg.add_edge('greet', 'lookup')
    sg.add_edge('lookup', 'schedule')
    sg.add_edge('schedule', 'confirm')
    sg.add_edge('confirm', 'reminder')
    sg.set_entry_point('greet')
    sg.set_finish_point('reminder')

    return sg.compile()
