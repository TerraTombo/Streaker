import tkinter as tk
from tkinter import messagebox
import sqlite3 
import datetime

# Datenbank einrichten
db = sqlite.connect("streaks.db")
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
