import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime, timedelta
import os

DATA_FILE = "streaks_data.json"
STYLE_FILE = "styles.json"

class StreakerApp:
    def __init__(self, root):
        self.root = root
        self.load_styles()
        self.apply_theme()

        self.root.title("Streaker")
        self.root.configure(bg=self.bg)

        self.streaks = []
        self.tasks = []
        self.load_data()

        self.create_widgets()
        self.update_list_display()


    def create_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        theme_frame = tk.Frame(self.root, bg=self.bg)
        theme_frame.pack(pady=5)

        tk.Label(theme_frame, text="Theme:", bg=self.bg, fg=self.title_fg).pack(side=tk.LEFT)

        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_menu = tk.OptionMenu(theme_frame, self.theme_var, *self.themes.keys(), command=self.change_theme)
        theme_menu.config(bg=self.button_bg, fg=self.button_fg)
        theme_menu["menu"].config(bg=self.button_bg, fg=self.button_fg)
        theme_menu.pack(side=tk.LEFT)

        label = tk.Label(self.root, text="Neue Streak/Task:", bg=self.bg, fg=self.title_fg, font=("Arial", 12, "bold"))
        label.pack()

        self.entry = tk.Entry(self.root, font=("Arial", 12))
        self.entry.pack(pady=5)

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack()

        btn_style = {"bg": self.button_bg, "fg": self.button_fg, "font": ("Arial", 10), "activebackground": self.button_bg}

        tk.Button(frame, text="Streak hinzufügen", command=self.add_streak, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Task hinzufügen", command=self.add_task, **btn_style).pack(side=tk.LEFT, padx=5)

        self.list_frame = tk.Frame(self.root, bg=self.bg)
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
        is_done = item.get("last_done", "") == self.today()

        # Hintergrundfarbe setzen:
        if is_done:
            bg_color = self.done_bg  # Erledigt = spezielle Farbe je nach Theme
        else:
            bg_color = self.bg       # Unerledigt = Standard-Theme-Hintergrund

        frame = tk.Frame(self.list_frame, bg=bg_color)
        frame.pack(fill="x", pady=2)

        name = item["name"]
        status = "✔️ Erledigt" if is_done else "❌ Offen"

        if not is_task:
            name += f" (Streak: {item['streak']})"

        label = tk.Label(frame, text=f"{name} | {status}", bg=bg_color, fg=self.task_fg)
        label.pack(side=tk.LEFT)

        btn = tk.Button(frame, text="Erledigt", command=lambda: self.mark_done(index, is_task),
                    bg=self.button_bg, fg=self.button_fg)
        btn.pack(side=tk.LEFT)

        del_btn = tk.Button(frame, text="Löschen", command=lambda: self.delete_item(index, is_task),
                        bg=self.button_bg, fg=self.button_fg)
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

    def load_styles(self):
        if os.path.exists(STYLE_FILE):
            with open(STYLE_FILE, "r") as f:
                data = json.load(f)
                self.themes = data.get("themes", {})
                self.current_theme = data.get("current_theme", "polar")
        else:
            # Fallback-Styles
            self.themes = {
                "default": {
                    "bg": "#333333", "fg": "#ffffff",
                    "button_bg": "#555555", "button_fg": "#ffffff"
                }
            }
            self.current_theme = "default"

    def apply_theme(self):
        theme = self.themes.get(self.current_theme, {})
        self.bg = theme.get("bg", "#333333")
        self.fg = theme.get("fg", "#ffffff")
        self.title_fg = theme.get("title_fg", self.fg)
        self.task_fg = theme.get("task_fg", self.fg)
        self.button_bg = theme.get("button_bg", "#555555")
        self.button_fg = theme.get("button_fg", "#ffffff")

        # Hintergrundfarbe für erledigte Tasks je nach Theme
        if self.current_theme == "polar":
            self.done_bg = "#000000"  # schwarz
        elif self.current_theme in ["jungle", "death_black"]:
            self.done_bg = "#ffffff"  # weiß
        else:
            self.done_bg = "#003300"  # fallback: dunkelgrün




    def change_theme(self, new_theme):
        self.current_theme = new_theme
        self.apply_theme()

        with open(STYLE_FILE, "w") as f:
            json.dump({
                "current_theme": self.current_theme,
                "themes": self.themes
            }, f, indent=2)

        self.root.configure(bg=self.bg)
        self.create_widgets()
        self.update_list_display()



if __name__ == "__main__":
    root = tk.Tk()
    app = StreakerApp(root)
    root.mainloop()
