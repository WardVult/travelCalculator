import json
from tkinter import messagebox

def save_to_json(data, file_path):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успіх", f"Дані збережено у файл {file_path}.")
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося зберегти файл: {e}")

def load_from_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося відкрити файл: {e}")
        return None
