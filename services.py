import json
from tkinter import messagebox

SERVICES_FILE = "services.json"

def load_services():
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Помилка", f"Файл {SERVICES_FILE} не знайдено.")
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Помилка", f"Помилка вмісту JSON у файлі {SERVICES_FILE}.")
        return []
