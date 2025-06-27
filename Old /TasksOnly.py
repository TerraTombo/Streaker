import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
from datetime import date

# Datenbank einrichten
db = sqlite3.connect("streaks.db")
cursor = db.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS tasks (
               if INTEGER PRIMARY KEY, 
               name TEXT,
               last_completed DATE
    )
""")
db.commit()


def update_ui():
    today = datetime.date.today().isoformat()

    #alle vorherigen Kinder zerstören
    for widget in frame.winfo_children():
        widget.destroy()
    #alle daten aus der Datenbank ziehen und darstellen
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    for task in tasks:
        task_date = date.fromisoformat(task[2])  # Konvertiere "YYYY-MM-DD" in ein Date-Objekt
        var = 0
        if task_date == today:
            var = tk.IntVar(1)

        chk = tk.Checkbutton(frame, text=task[1], variable=var,
                             command=lambda t=task[0], v=var: toggle_task(t, v, today))
        chk.pack(anchor='w', pady=2)

    cursor.execute("SELECT * FROM streaks")
    date_label.config(text=f"{datetime.date.today().strftime('%d.%m.%Y')}")

def toggle_task(task_id, var, today):
    if var.get() == 1:
        cursor.execute("UPDATE tasks SET last_completed=? WHERE id=?", (today, task_id))
    else:
        cursor.execute("UPDATE tasks SET last_completed=completed_before WHERE id=?", (task_id))
    db.commit()
    update_ui()

def add_task():
    task_name = task_entry.get().strip()
    if task_name:
        cursor.execute("INSERT INTO tasks (name) VALUES (?)", (task_name,))
        db.commit()
        task_entry.delete(0, tk.END)
        update_ui()

def delete_task():
    task_name = task_entry.get().strip()
    if task_name:
        cursor.execute("DELETE FROM tasks WHERE name = ?", (task_name,))
        db.commit()
        task_entry.delete(0, tk.END)
        update_ui()

def complete_day():
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed=1")
    completed_tasks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    if completed_tasks == total_tasks and total_tasks > 0:
        cursor.execute("UPDATE streaks SET count = count + 1, last_completed = ? WHERE id=1", (today,))
        messagebox.showinfo("Erfolg!", "Alle Aufgaben erledigt! Streak erhöht!")
    else:
        cursor.execute("UPDATE streaks SET count = 0, last_completed = ? WHERE id=1", (today,))
        messagebox.showinfo("Fehlgeschlagen", "Nicht alle Aufgaben erledigt. Streak zurückgesetzt.")
    db.commit()
    update_ui()


# GUI erstellen
root = tk.Tk()
root.title("Daily Streak Tracker")
root.geometry("400x500")

date_label = tk.Label(root, text="", font=("Arial", 12))
date_label.pack()

frame = tk.Frame(root)
frame.pack(pady=10)

streak_label = tk.Label(root, text="Streak: 0", font=("Arial", 14))
streak_label.pack()

task_entry = tk.Entry(root)
task_entry.pack()
tk.Button(root, text="Add Task", command=add_task).pack()
tk.Button(root, text="Add Streak", command=add_streak).pack()
tk.Button(root, text="Delete Task/Streak", command=delete_task).pack()
tk.Button(root, text="Tag abschließen", command=complete_day).pack()

update_ui()
root.mainloop()