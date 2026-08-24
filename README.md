# Healthcare Appointment Manager

A full-stack healthcare appointment management system built with **Flask, SQLite, SQLAlchemy, HTML, CSS, JavaScript, and Ollama AI**. The platform connects patients, doctors, and administrators through a centralized healthcare portal.

## Features

### 👤 Patient Module

* Patient registration and login
* Browse available doctors
* Select appointment date and time
* View real-time available appointment slots
* Book appointments
* Provide symptoms/reason for visit
* View upcoming and previous appointments
* Cancel appointments
* View appointment status
* View post-visit information
* Receive medication reminders based on prescription frequency

### 👨‍⚕️ Doctor Module

* Doctor login and dashboard
* View scheduled appointments
* View patient information and symptoms
* AI-powered pre-visit summaries
* Suggested questions for consultation
* Confirm or cancel appointments
* Complete consultations
* Add:

  * Diagnosis
  * Post-visit notes
  * Prescription
  * Follow-up instructions
* Generate patient-friendly post-visit summaries using AI
* Regenerate pre-visit AI summaries when required

### 🛠️ Admin Module

* Admin authentication
* Manage doctors
* Add doctors
* Edit doctor information
* Configure doctor working hours
* Configure appointment slot duration
* Manage doctor leave
* Prevent appointment booking during doctor leave

### 🤖 AI Features

The application uses **Ollama with Llama 3.2 (3B)** for local AI processing.

#### Pre-Visit AI Summary

Patient-provided symptoms are converted into:

* Chief complaint
* Key symptoms
* Duration
* Urgency
* Three suggested questions for the doctor

Example:

```text
Patient Symptoms
        ↓
Ollama / Llama 3.2
        ↓
Pre-Visit Summary
        ↓
Doctor Consultation
```

The AI is instructed not to diagnose the patient or recommend medication.

#### Post-Visit AI Summary

Doctor-provided information is converted into a simple patient-friendly summary.

```text
Diagnosis
Post-Visit Notes
Prescription
Follow-up Instructions
        ↓
Ollama / Llama 3.2
        ↓
Patient-Friendly Summary
```

The AI does not modify medication names, dosage, frequency, or doctor's instructions.

### 💊 Medication Reminder System

The system can create medication reminders based on the prescription frequency.

Example:

```text
Prescription:
Paracetamol 500mg
1 tablet twice daily for 5 days

        ↓

Medication Reminders:

08:00 AM — Paracetamol 500mg
08:00 PM — Paracetamol 500mg
```

Patients can view their medication schedule and mark medications as taken.

---

## Appointment Workflow

```text
Patient
   │
   ▼
Select Doctor
   │
   ▼
Select Date
   │
   ├── Doctor on Leave ──► Booking Rejected
   │
   ▼
Available Time Slots
   │
   ▼
Enter Symptoms
   │
   ▼
Book Appointment
   │
   ▼
AI Pre-Visit Summary
   │
   ▼
Doctor Reviews Appointment
   │
   ├── Confirm
   ├── Cancel
   │
   ▼
Consultation
   │
   ▼
Doctor Adds Post-Visit Notes
   │
   ├── Diagnosis
   ├── Notes
   ├── Prescription
   └── Follow-up Instructions
   │
   ▼
AI Patient-Friendly Summary
   │
   ▼
Appointment Completed
   │
   ▼
Medication Reminders
```

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Font Awesome
* Google Fonts

### Backend

* Python
* Flask
* Flask Blueprints
* SQLAlchemy

### Database

* SQLite
* SQLAlchemy ORM

### AI

* Ollama
* Llama 3.2:3b
* JSON-based AI responses

### Development

* Python Virtual Environment
* Git/GitHub

---

## Project Structure

```text
Healthcare/
│
├── app.py
├── config.py
├── extensions.py
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── doctor.py
│   ├── appointment.py
│   ├── doctor_leave.py
│   ├── symptom.py
│   ├── ai_summary.py
│   ├── post_visit.py
│   └── medication_reminder.py
│
├── routes/
│   ├── auth.py
│   ├── appointments.py
│   ├── doctor.py
│   └── admin.py
│
├── services/
│   └── ai_service.py
│
├── templates/
│   ├── auth/
│   ├── patient/
│   ├── doctor/
│   └── admin/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── instance/
│   └── healthcare.db
│
├── requirements.txt
└── README.md
```

> Adjust the folder names if your actual project uses a different structure.

---

## Database Models

The main entities are:

```text
User
 │
 ├── Patient
 └── Doctor

Doctor
 │
 ├── Appointments
 └── Doctor Leave

Appointment
 │
 ├── Symptoms
 ├── AI Summary
 └── Post-Visit Record
          │
          └── Medication Reminders
```

### Post Visit Record

Stores:

* Appointment
* Doctor
* Patient
* Diagnosis
* Post-visit notes
* Prescription
* Follow-up instructions
* AI-generated patient summary

### Medication Reminder

Stores:

* Medication
* Dosage
* Frequency
* Reminder time
* Start date
* End date
* Patient
* Reminder status

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd Healthcare
```

### 2. Create Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama on your system and download the required model:

```bash
ollama pull llama3.2:3b
```

Start Ollama if it is not already running:

```bash
ollama serve
```

### 5. Run the Application

```bash
python app.py
```

The application should be available at:

```text
http://127.0.0.1:5000
```

---

## AI Configuration

The application uses the Ollama Python package:

```python
import ollama
```

The AI service calls:

```python
ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)
```

No external OpenAI API key is required when using the local Ollama setup.

---

## Appointment Slot Management

Doctors have configurable:

```text
Working Start Time
Working End Time
Slot Duration
```

For example:

```text
Working Hours: 09:00 - 13:00
Slot Duration: 30 minutes
```

The system automatically generates:

```text
09:00 - 09:30
09:30 - 10:00
10:00 - 10:30
10:30 - 11:00
...
```

Already booked slots are removed from the available slots.

Cancelled appointments do not block the slot.

---

## Doctor Leave Management

Before displaying or booking a slot, the system checks whether the doctor has leave on the selected date.

If the doctor is on leave:

```text
Doctor is on leave on this date.
```

The appointment cannot be booked.

The backend performs the leave check again during booking, preventing users from bypassing the frontend validation.

---

## Appointment Status

Appointments can have the following statuses:

```text
booked
confirmed
completed
cancelled
```

Typical flow:

```text
Booked
  ↓
Confirmed
  ↓
Completed
```

or:

```text
Booked
  ↓
Cancelled
```

---

## API Endpoints

### Patient

```text
GET  /appointments/book-page
GET  /appointments/available-slots
GET  /appointments/slots
POST /appointments/book
GET  /appointments/my-appointments
```

### Doctor

```text
GET  /appointments/doctor
POST /appointments/<appointment_id>/regenerate-summary
POST /appointments/<appointment_id>/status
POST /appointments/<appointment_id>/post-visit
```

### Example: Book Appointment

```json
{
    "doctor_id": 1,
    "appointment_date": "2026-08-25",
    "start_time": "10:00",
    "end_time": "10:30",
    "symptoms": "Headache and mild fever"
}
```

### Example Response

```json
{
    "success": true,
    "status": "confirmed",
    "message": "Booking confirmed successfully.",
    "appointment_id": 15
}
```

---

## Security & Validation

The system includes:

* Session-based authentication
* Role-based access control
* Patient/doctor authorization checks
* Appointment ownership verification
* Doctor leave validation
* Duplicate slot prevention
* Database integrity handling
* Input validation
* AI failure handling

AI failure does not prevent an appointment or post-visit record from being saved.

---

## AI Safety

The AI is used as a **support tool**, not as an autonomous medical decision-maker.

Pre-visit AI:

```text
✓ Summarizes patient-provided information
✓ Identifies reported symptoms
✓ Identifies reported duration
✓ Generates consultation questions

✗ Does not diagnose
✗ Does not prescribe medication
✗ Does not invent symptoms
```

Post-visit AI:

```text
✓ Simplifies doctor's information
✓ Creates a patient-friendly explanation

✗ Does not create a new diagnosis
✗ Does not recommend additional medication
✗ Does not modify prescription instructions
```

---

## Future Enhancements

* Email medication reminders
* Browser notifications
* SMS reminders
* Medication adherence tracking
* Patient medical history
* Doctor availability calendar
* Appointment rescheduling
* Digital prescription download
* PDF medical reports
* Admin analytics dashboard
* Appointment statistics
* Secure deployment with HTTPS
* Automated reminder scheduler using APScheduler/Celery

---

## Project Objective

The objective of the Healthcare Appointment Manager is to provide a centralized platform for managing healthcare appointments while reducing administrative effort and improving communication between patients and doctors.

The system combines **appointment management, AI-assisted clinical support, post-visit documentation, and medication reminders** into one integrated healthcare workflow.

---

## Disclaimer

This project is an academic/software development project. The AI functionality is intended to provide administrative and informational support and **should not replace professional medical judgment, diagnosis, or treatment**.
