# Medical Appointment Scheduling AI Agent

A complete multi-agent scheduling system using LangChain + LangGraph with Streamlit UI.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run src/app.py
```

## Assignment Deliverables

### Core Features Implemented
- **Patient Greeting**: Collects name, DOB, doctor, location
- **Patient Lookup**: Detects new vs returning patients
- **Smart Scheduling**: 60min slots for new patients, 30min for returning
- **Insurance Collection**: Captures carrier, member ID, group number
- **Appointment Confirmation**: Sends intake form via email
- **Reminder System**: 3 automated SMS reminders

### Technical Implementation
- **LangChain + LangGraph**: Multi-agent orchestration
- **Streamlit UI**: Chatbot interface with admin panel
- **Data Integration**: CSV/Excel I/O with pandas
- **Email/SMS Simulation**: Console-based messaging
- **Indian Names**: Hindu, Muslim, Christian patient data

### Files Structure
```
ai-healthcare-scheduler/
├── src/
│   ├── agents/agents.py          # LangGraph agents
│   ├── utils/io_utils.py         # Data utilities
│   ├── app.py                    # Streamlit UI
│   └── data_gen.py               # Data generator
├── patients.csv                  # 50 synthetic patients
├── doctor_schedule.xlsx          # Doctor schedules
├── appointments_export.xlsx      # Appointment records
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Usage Example

1. **Enter patient info**: `Name: Arjun Sharma, DOB: 1990-08-23, Dr: Arjun Sharma, Location: Mumbai Central`
2. **Enter insurance**: `Carrier: Star Health; Member: ABC12345; Group: 987654`
3. **Watch workflow**: Greeting -> Lookup -> Scheduling -> Insurance -> Confirmation -> Reminders

## Features Demonstrated

- **Multi-Agent Architecture**: 6 specialized agents working together
- **Natural Language Processing**: Extracts structured data from user input
- **Business Logic**: Smart appointment duration based on patient type
- **File Operations**: DOCX email attachments, Excel exports
- **Error Handling**: Graceful handling of edge cases
- **Admin Interface**: Real-time appointment tracking

## Technical Stack

- **LangChain**: Agent framework
- **LangGraph**: Multi-agent orchestration
- **Streamlit**: Web UI
- **Pandas**: Data manipulation
- **OpenPyXL**: Excel operations
- **Python-DOCX**: Document handling

## Notes

- Email/SMS are simulated in console output
- All data is synthetic for demonstration
- No external API keys required
- Fully executable end-to-end workflow
