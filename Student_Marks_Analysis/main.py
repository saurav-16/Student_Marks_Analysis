import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import csv
import os
from utils import calculate_total_and_grade

DATABASE = "student_marks.db"
subject_count = 0
mark_entries = []


def get_connection():
    return sqlite3.connect(DATABASE)


# Create the table based on the number of subjects
def create_table(subject_count):
    with get_connection() as conn:
        cursor = conn.cursor()
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


# Update subjects input fields dynamically
def update_subjects():
    global mark_entries
    for widget in mark_entries:
        widget.destroy()

    mark_entries = []
    for i in range(subject_count):
        tk.Label(root, text=f"Subject {i + 1}:", bg="#f0f4f7").grid(row=1, column=i * 2)
        entry = tk.Entry(root, width=5)
        entry.grid(row=2, column=i * 2, padx=5)
        mark_entries.append(entry)


# Show all students in the table
def show_students():
    for row in tree.get_children():
        tree.delete(row)

    students = fetch_all_students(subject_count)
    for student in students:
        reg_no, name, *marks, total, avg, grade = student
        tree.insert('', tk.END, values=(reg_no, name, *marks, total, avg, grade))


# Add student
def on_add_student():
    reg_no = reg_no_entry.get()
    name = name_entry.get()
    marks = [entry.get() for entry in mark_entries]

    if not reg_no or not name:
        messagebox.showerror("Error", "Register number and name are required.")
        return

    try:
        marks = [int(mark) if mark.isdigit() else 0 for mark in marks]
    except ValueError:
        messagebox.showerror("Error", "Please enter valid marks.")
        return

    insert_student(reg_no, name, marks)

    reg_no_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    for entry in mark_entries:
        entry.delete(0, tk.END)

    show_students()


# Delete student
def on_delete_student():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "No student selected.")
        return

    reg_no = tree.item(selected[0])['values'][0]
    delete_student(reg_no)
    show_students()


# Export data to CSV
def export_data():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(students)')
        columns = [info[1] for info in cursor.fetchall()]
        cursor.execute('SELECT * FROM students')
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("Export", "No data to export.")
            return

        with open("students_data.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(rows)

        messagebox.showinfo("Export", f"Data exported to {os.path.abspath('students_data.csv')}")


# Main GUI setup
def start_gui():
    global reg_no_entry, name_entry, mark_entries, tree, root

    root = tk.Tk()
    root.title("Student Marks Analysis System")
    root.geometry("1200x600")
    root.configure(bg="#f0f4f7")

    tk.Label(root, text="Register No:", bg="#f0f4f7").grid(row=0, column=0, padx=10, pady=10)
    reg_no_entry = tk.Entry(root)
    reg_no_entry.grid(row=0, column=1, padx=10)

    tk.Label(root, text="Name:", bg="#f0f4f7").grid(row=0, column=2)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=3, padx=10)

    # Subject count input
    subject_label = tk.Label(root, text="Number of Subjects (up to 10):", bg="#f0f4f7")
    subject_label.grid(row=0, column=4)
    subject_count_entry = tk.Entry(root, width=5)
    subject_count_entry.grid(row=0, column=5, padx=10)

    # Button to update subjects
    def update_subjects_count():
        global subject_count
        try:
            subject_count = int(subject_count_entry.get())
            if subject_count < 1 or subject_count > 10:
                raise ValueError
            update_subjects()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number between 1 and 10.")

    update_button = tk.Button(root, text="Update Subjects", command=update_subjects_count)
    update_button.grid(row=0, column=6, padx=10)

    # Buttons for actions
    tk.Button(root, text="Add Student", bg="#4caf50", fg="white", command=on_add_student).grid(row=3, column=0, pady=20)
    tk.Button(root, text="Delete Student", bg="#f44336", fg="white", command=on_delete_student).grid(row=3, column=1)
    tk.Button(root, text="Export Data", bg="#2196f3", fg="white", command=export_data).grid(row=3, column=2)

    # Treeview setup
    columns = ["Register No", "Name"] + [f"Subject {i+1}" for i in range(subject_count)] + ["Total", "Average", "Grade"]
    tree = ttk.Treeview(root, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    tree.grid(row=4, column=0, columnspan=subject_count + 2, padx=10, pady=10)

    show_students()
    root.mainloop()


# ------------------ Entry Point ------------------ #
if __name__ == "__main__":
    try:
        subject_count = int(input("Enter number of subjects (1 to 10): "))
        if subject_count < 1 or subject_count > 10:
            raise ValueError
    except ValueError:
        print("Please enter a valid number between 1 and 10.")
        exit()

    create_table(subject_count)
    start_gui()
