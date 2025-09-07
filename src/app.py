import streamlit as st
from typing import Optional
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agents.agents import greeting_agent, insurance_agent, build_graph
from utils.io_utils import load_patients, load_schedule

st.set_page_config(page_title="Medical Scheduling AI Agent", layout="wide")

if 'state' not in st.session_state:
    st.session_state.state = {}
    st.session_state.graph = build_graph()

state = st.session_state.state

st.title("Medical Appointment Scheduling AI Agent")

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Chatbot")
    
    # Add clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.state = {}
        st.rerun()

    for msg in state.get('messages', []):
        role = 'assistant' if msg.get('type') == 'ai' else 'user'
        st.chat_message(role).write(msg.get('content', ''))

    placeholder = (
        "Try: 'Name: Arjun Sharma', 'DOB: 1990-08-23', 'Dr: Arjun Sharma', "
        "'Location: Mumbai Central'. Then: 'Carrier: Star Health; Member: ABC12345; Group: 987654'"
    )
    user_input: Optional[str] = st.chat_input(placeholder)

    if user_input:
        state = greeting_agent(state, user_input)
        if any(k in user_input.lower() for k in ['carrier', 'member', 'group']):
            state = insurance_agent(state, user_input)
        try:
            if state.get('name') and state.get('dob') and state.get('doctor') and state.get('location') and state.get('is_new_patient') is None:
                state = st.session_state.graph.invoke(state)
        except FileNotFoundError as e:
            state.setdefault('messages', []).append({'type':'ai','content': f"Setup incomplete: {e}. Run data generator."})
        except Exception as e:
            state.setdefault('messages', []).append({'type':'ai','content': f"An error occurred: {e}"})
        st.session_state.state = state
        st.rerun()

with col2:
    st.subheader("Admin Panel")
    if st.button("Refresh Data"):
        st.rerun()
    try:
        patients = load_patients()
        st.metric("Patients", len(patients))
    except Exception as e:
        st.warning(f"Patients not found: {e}")
    try:
        schedule = load_schedule()
        booked = (~schedule['available']).sum()
        st.metric("Booked Appointments", int(booked))
        st.dataframe(schedule[schedule['available'] == False].tail(10), use_container_width=True)
    except Exception as e:
        st.warning(f"Schedule not found: {e}")

st.caption("💡 Tip: First provide Name, DOB, Dr, Location. Then provide insurance details: Carrier, Member, Group.")
