import streamlit as st


import mysql.connector
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306))
    )

conn = get_db_connection()
c = conn.cursor()

# # Table creation (run once at startup)
# def create_tables():
#     c.execute('''CREATE TABLE IF NOT EXISTS students (
#         roll_no VARCHAR(20) PRIMARY KEY,
#         name VARCHAR(100) NOT NULL,
#         class VARCHAR(10) NOT NULL
#     )''')
#     c.execute('''CREATE TABLE IF NOT EXISTS attendance (
#         student_id VARCHAR(20) PRIMARY KEY,
#         date DATE NOT NULL,
#         status ENUM('Present', 'Absent') NOT NULL,
#         FOREIGN KEY(student_id) REFERENCES students(roll_no)
#     )''')
#     c.execute('''CREATE TABLE IF NOT EXISTS marks (
#         student_id VARCHAR(20) PRIMARY KEY,
#         subject VARCHAR(50) NOT NULL,
#         marks INT NOT NULL,
#         FOREIGN KEY(student_id) REFERENCES students(roll_no)
#     )''')
#     conn.commit()

# create_tables()

# Helper functions

def add_student(roll_no, name, class_):
    try:
        c.execute('INSERT INTO students (roll_no, name, class) VALUES (%s, %s, %s)', (roll_no, name, class_))
        conn.commit()
        return True, "Student added successfully."
    except mysql.connector.IntegrityError:
        return False, "Roll No already exists."


def get_students():
    c.execute('SELECT roll_no, name, class FROM students')
    return c.fetchall()


def mark_attendance(student_id, status):
    today = date.today().isoformat()
    c.execute('SELECT * FROM attendance WHERE student_id=%s AND date=%s', (student_id, today))
    if c.fetchone():
        return False, "Attendance already marked for today."
    c.execute('INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)', (student_id, today, status))
    conn.commit()
    return True, "Attendance marked."


def add_marks(student_id, subject, marks):
    c.execute('INSERT INTO marks (student_id, subject, marks) VALUES (%s, %s, %s)', (student_id, subject, marks))
    conn.commit()
    return True, "Marks added."


def get_attendance_history(student_id):
    c.execute('SELECT date, status FROM attendance WHERE student_id=%s ORDER BY date DESC', (student_id,))
    return c.fetchall()


def get_attendance_percentage(student_id):
    c.execute('SELECT COUNT(*) FROM attendance WHERE student_id=%s', (student_id,))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM attendance WHERE student_id=%s AND status='Present'", (student_id,))
    present = c.fetchone()[0]
    return (present / total * 100) if total > 0 else 0


def get_marks(student_id):
    c.execute('SELECT subject, marks FROM marks WHERE student_id=%s', (student_id,))
    return c.fetchall()

def get_pass_fail(student_id):
    marks = get_marks(student_id)
    return "Pass" if all(m[1] >= 40 for m in marks) and marks else "Fail"

# Streamlit UI
st.title("Student Attendance & Marks Portal")

menu = st.sidebar.selectbox("Menu", ["Add Student", "Mark Attendance", "Add Marks", "View Attendance", "View Marks"])

if menu == "Add Student":
    with st.form("add_student_form"):
        roll_no = st.text_input("Roll No")
        name = st.text_input("Name")
        class_ = st.selectbox("Class", ["A", "B", "C", "D"])
        submitted = st.form_submit_button("Add Student")
        if submitted:
            success, msg = add_student(roll_no, name, class_)
            if success:
                st.success(msg)
            else:
                st.error(msg)

elif menu == "Mark Attendance":
    section = st.selectbox("Select Section", ["A", "B", "C", "D"])
    students = [s for s in get_students() if s[2] == section]
    student_map = {f"{s[0]} - {s[1]} ({s[2]})": s[0] for s in students}
    if student_map:
        with st.form("attendance_form"):
            student = st.selectbox("Select Student", list(student_map.keys()))
            status = st.radio("Attendance Status", ["Present", "Absent"])
            submitted = st.form_submit_button("Mark Attendance")
            if submitted:
                success, msg = mark_attendance(student_map[student], status)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

            st.markdown("---")
            if 'show_edit_attendance' not in st.session_state:
                st.session_state['show_edit_attendance'] = False
            if st.form_submit_button("Edit Attendance", key="show_edit_attendance_btn"):
                st.session_state['show_edit_attendance'] = True

            if st.session_state['show_edit_attendance']:
                st.subheader("Edit Attendance Record")
                from datetime import datetime
                edit_date = st.date_input("Select Date", value=datetime.today(), key="edit_attendance_date")
                roll_no = student_map[student]
                history = get_attendance_history(roll_no)
                # Fetch current status for the selected date
                current_status = None
                for h in history:
                    if str(h[0]) == str(edit_date):
                        current_status = h[1]
                        break
                if current_status:
                    new_status = st.radio("Update Status", ["Present", "Absent"], index=0 if current_status=="Present" else 1, key="edit_attendance_status")
                    update_submitted = st.form_submit_button("Update Attendance", key="update_attendance_btn")
                    if update_submitted:
                        c.execute('UPDATE attendance SET status=%s WHERE student_id=%s AND date=%s', (new_status, roll_no, edit_date))
                        conn.commit()
                        st.success(f"Attendance updated to {new_status} for {edit_date}.")
                        st.session_state['show_edit_attendance'] = False
                else:
                    st.info("No attendance record for this date.")
    else:
        st.info(f"No students available in section {section}.")

elif menu == "Add Marks":
    section = st.selectbox("Select Section", ["A", "B", "C", "D"])
    students = [s for s in get_students() if s[2] == section]
    student_map = {f"{s[0]} - {s[1]} ({s[2]})": s[0] for s in students}
    subjects = ["Maths", "Science", "English", "Social Studies"]
    if student_map:
        with st.form("marks_form"):
            student = st.selectbox("Select Student", list(student_map.keys()))
            subject = st.selectbox("Subject", subjects)
            marks = st.number_input("Marks", min_value=0, max_value=100)
            submitted = st.form_submit_button("Add Marks")
            if submitted:
                success, msg = add_marks(student_map[student], subject, marks)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    else:
        st.info(f"No students available in section {section}.")

elif menu == "View Attendance":
    section = st.selectbox("Select Section", ["A", "B", "C", "D"])
    students = [s for s in get_students() if s[2] == section]
    student_map = {f"{s[0]} - {s[1]} ({s[2]})": s[0] for s in students}
    if student_map:
        student = st.selectbox("Select Student", list(student_map.keys()))
        roll_no = student_map[student]
        history = get_attendance_history(roll_no)
        st.dataframe(history, use_container_width=True)
        percent = get_attendance_percentage(roll_no)
        st.write(f"Attendance %: {percent:.2f}")
    else:
        st.info(f"No students available in section {section}.")

elif menu == "View Marks":
    section = st.selectbox("Select Section", ["A", "B", "C", "D"])
    students = [s for s in get_students() if s[2] == section]
    student_map = {f"{s[0]} - {s[1]} ({s[2]})": s[0] for s in students}
    if student_map:
        student = st.selectbox("Select Student", list(student_map.keys()))
        marks = get_marks(student_map[student])
        st.dataframe(marks, use_container_width=True)
        status = get_pass_fail(student_map[student])
        st.write(f"Status: {status}")
    else:
        st.info(f"No students available in section {section}.")
