import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime, timedelta
import os

DATA_FILE = "streaks_data.json"

class StreakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Streaker")
        self.root.configure(bg="#333333")

        self.streaks = []
        self.tasks = []
        self.load_data()  # lädt Daten + prüft Streaks

        self.create_widgets()
        self.update_list_display()  # zeigt sie direkt beim Start


    def create_widgets(self):
        label = tk.Label(self.root, text="Neue Streak/Task:", bg="#333333", fg="#FFFFFF", font=("Arial", 12, "bold"))
        label.pack()

        self.entry = tk.Entry(self.root, font=("Arial", 12))
        self.entry.pack(pady=5)

        # Buttons in einem hellgrauen Frame
        frame = tk.Frame(self.root, bg="#333333")
        frame.pack()

        btn_style = {"bg": "#333333", "fg": "white", "font": ("Arial", 10), "activebackground": "#333333"}

        tk.Button(frame, text="Streak hinzufügen", command=self.add_streak, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Task hinzufügen", command=self.add_task, **btn_style).pack(side=tk.LEFT, padx=5)

        self.list_frame = tk.Frame(self.root, bg="#333333")
        self.list_frame.pack(pady=10)


    def update_list_display(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        tk.Label(self.list_frame, text="--- Streaks ---").pack()

        for i, item in enumerate(self.streaks):
            self.display_item(item, i, is_task=False)

        tk.Label(self.list_frame, text="--- Tasks ---").pack()

        for i, item in enumerate(self.tasks):
            self.display_item(item, i, is_task=True)

    def display_item(self, item, index, is_task=False):
        frame = tk.Frame(self.list_frame)
        frame.pack(fill="x", pady=2)

        name = item["name"]
        status = "✔️ Erledigt" if item.get("last_done", "") == self.today() else "❌ Offen"

        if not is_task:
            name += f" (Streak: {item['streak']})"

        label = tk.Label(frame, text=f"{name} | {status}")
        label.pack(side=tk.LEFT)

        btn = tk.Button(frame, text="Erledigt", command=lambda: self.mark_done(index, is_task))
        btn.pack(side=tk.LEFT)

        del_btn = tk.Button(frame, text="Löschen", command=lambda: self.delete_item(index, is_task))
        del_btn.pack(side=tk.LEFT)

    def mark_done(self, index, is_task):
        today = self.today()
        if is_task:
            self.tasks[index]["last_done"] = today
        else:
            streak = self.streaks[index]
            yesterday = self.date_str(-1)
            last_done = streak.get("last_done", "")
            if last_done == today:
                messagebox.showinfo("Hinweis", "Heute bereits erledigt!")
                return
            elif last_done == yesterday:
                streak["streak"] += 1
            else:
                streak["streak"] = 1  # zurücksetzen

            streak["last_done"] = today

        self.save_data()
        self.update_list_display()

    def delete_item(self, index, is_task):
        if is_task:
            del self.tasks[index]
        else:
            del self.streaks[index]

        self.save_data()
        self.update_list_display()

    def add_streak(self):
        name = self.entry.get().strip()
        if name:
            self.streaks.append({"name": name, "streak": 0, "last_done": ""})
            self.entry.delete(0, tk.END)
            self.save_data()
            self.update_list_display()

    def add_task(self):
        name = self.entry.get().strip()
        if name:
            self.tasks.append({"name": name, "last_done": ""})
            self.entry.delete(0, tk.END)
            self.save_data()
            self.update_list_display()

    def today(self):
        return datetime.now().strftime("%Y-%m-%d")

    def date_str(self, offset_days):
        return (datetime.now() + timedelta(days=offset_days)).strftime("%Y-%m-%d")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.streaks = data.get("streaks", [])
                self.tasks = data.get("tasks", [])
                self.check_streaks()

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump({"streaks": self.streaks, "tasks": self.tasks}, f, indent=2)

    def check_streaks(self):
        yesterday = self.date_str(-1)
        today = self.today()
        for streak in self.streaks:
            last_done = streak.get("last_done", "")
            if last_done not in [yesterday, today]:
                streak["streak"] = 0  # zurücksetzen

if __name__ == "__main__":
    root = tk.Tk()
    app = StreakerApp(root)
    root.mainloop()
