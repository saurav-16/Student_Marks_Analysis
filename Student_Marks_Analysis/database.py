import sqlite3

DATABASE = "student_marks.db"

# Get a connection to the database
def get_connection():
    return sqlite3.connect(DATABASE)

# Create the table based on the number of subjects
def create_table(subject_count):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Creating columns dynamically for each subject (up to subject_count)
        columns = ", ".join([f"S{i+1}" for i in range(subject_count)])
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS students (
                reg_no TEXT PRIMARY KEY,
                name TEXT,
                {columns},
                total INTEGER,
                avg REAL,
                grade TEXT
            )
        """)
        conn.commit()

# Insert student data
def insert_student(reg_no, name, marks):
    total = sum(marks)
    avg = total / len(marks)
    grade = calculate_grade(avg)
    with get_connection() as conn:
        cursor = conn.cursor()
        # Dynamically create columns based on the subject count
        columns = ", ".join([f"S{i+1}" for i in range(len(marks))])
        cursor.execute(f"""
            INSERT INTO students (reg_no, name, {columns}, total, avg, grade)
            VALUES (?, ?, {', '.join(['?']*len(marks))}, ?, ?, ?)
        """, (reg_no, name, *marks, total, avg, grade))
        conn.commit()

# Fetch all student data
def fetch_all_students(subject_count):
    with get_connection() as conn:
        cursor = conn.cursor()
        # Dynamically fetch columns based on the subject count
        columns = ["reg_no", "name"] + [f"S{i+1}" for i in range(subject_count)] + ["total", "avg", "grade"]
        cursor.execute(f"SELECT {', '.join(columns)} FROM students")
        return cursor.fetchall()

# Delete student by registration number
def delete_student(reg_no):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE reg_no = ?", (reg_no,))
        conn.commit()

# Calculate grade based on average marks
def calculate_grade(avg):
    if avg >= 90:
        return "A+"
    elif avg >= 80:
        return "A"
    elif avg >= 70:
        return "B+"
    elif avg >= 60:
        return "B"
    elif avg >= 50:
        return "C"
    elif avg >= 40:
        return "D"
    else:
        return "F"

