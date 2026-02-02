# Student Attendance & Marks Portal

A Streamlit web application to manage student attendance and marks using a database.

## Features
- Add student details (Roll No, Name, Class)
- Mark daily attendance (Present/Absent)
- Add subject-wise marks
- View attendance history
- Calculate total attendance %
- Show pass/fail status

## Streamlit Concepts Used
- `st.form()` – group inputs
- `st.selectbox()` – select class/subject
- `st.radio()` – attendance status
- `st.success()`, `st.error()` – feedback
- `st.session_state` – login/session handling
- `st.dataframe()` – display records

## Database Tables
- students(id, roll_no, name, class)
- attendance(id, student_id, date, status)
- marks(id, student_id, subject, marks)

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Initialize database: `sqlite3 database.db < database.sql`
3. Run app: `streamlit run app.py`

## Screenshots
See the `screenshots/` folder for UI examples.
