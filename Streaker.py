import tkinter as tk
from tkinter import messagebox
import sqlite3 
import datetime

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
cursor.execute("""
               CREATE TABLE IF NOT EXISTS streak (
               if INTEGER PRIMARY KEY, 
               name TEXT,
               streak INTEGER DEFAULT 0,
               last_completed DATE
    )
""")
db.commit()


def update_ui():
    for widget in frame.winfo_children():
        widget.destroy()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM streaks")
    streaks = cursor.fetchall()

    for task in tasks:
        var = tk.IntVar(value=task[2])
        chk = tk.Checkbutton(frame, text=task[1], variable=var,
                             command=lambda t=task[0], v=var: toggle_task(t, v))
        chk.pack(anchor='w', pady=2)

    for streak in streaks:
        var = tk.IntVar(value=streak[2])
        chk = tk.Checkbutton(frame, text=streak[1], variable=var,
                             command=lambda t=streak[0], v=var: toggle_task(t, v))
        chk.pack(anchor='w', pady=2)

    cursor.execute("SELECT count FROM streak WHERE id=1")
    streak = cursor.fetchone()
    streak_count = streak[0] if streak else 0
    flame_emoji = " 🔥" if streak_count > 0 else ""
    streak_label.config(text=f"Streak: {streak_count}{flame_emoji}")

    date_label.config(text=f"Heute: {datetime.date.today().strftime('%d.%m.%Y')}")


# task beendet oder nicht?
def toggle_task(task_id, var):
    today = datetime.date.today().isoformat()
    new_status = var.get()
    if new_status == 1:
        cursor.execute("UPDATE tasks SET last_completed=? WHERE id=?", (today, task_id))
    db.commit()
    update_ui()

def add_task():
    task_name = task_entry.get().strip()
    if task_name:
        cursor.execute("INSERT INTO tasks (name) VALUES (?)", (task_name,))
        db.commit()
        task_entry.delete(0, tk.END)
        update_ui()

def add_streak():
    task_name = task_entry.get().strip()
    if task_name:
        cursor.execute("INSERT INTO streaks (name) VALUES (?)", (task_name,))
        db.commit()
        task_entry.delete(0, tk.END)
        update_ui()

def delete_task():
    task_name = task_entry.get().strip()
    if task_name:
        cursor.execute("DELETE FROM tasks WHERE name = ?", (task_name,))
        cursor.execute("DELETE FROM streaks WHERE name = ?", (task_name,))
        db.commit()
        task_entry.delete(0, tk.END)
        update_ui()

def complete_day():
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT last_completed FROM streak WHERE id=1")
    last_date = cursor.fetchone()

    if last_date and last_date[0] == today:
        messagebox.showinfo("Info", "Streak wurde heute bereits aktualisiert!")
        return

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed=1")
    completed_tasks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    if completed_tasks == total_tasks and total_tasks > 0:
        cursor.execute("UPDATE streak SET count = count + 1, last_completed = ? WHERE id=1", (today,))
        messagebox.showinfo("Erfolg!", "Alle Aufgaben erledigt! Streak erhöht!")
    else:
        cursor.execute("UPDATE streak SET count = 0, last_completed = ? WHERE id=1", (today,))
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