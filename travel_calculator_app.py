import tkinter as tk
from tkinter import messagebox, filedialog
from services import load_services
from utils import save_to_json, load_from_json
from math import ceil

class TravelCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Розрахунок вартості подорожі")
        self.services = load_services()
        self.selected_services = []

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Кількість людей у номерах SGL").grid(row=0, column=0, sticky="w")
        self.sgl_count_entry = tk.Entry(self.root)
        self.sgl_count_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Кількість людей у номерах TWIN").grid(row=1, column=0, sticky="w")
        self.twin_count_entry = tk.Entry(self.root)
        self.twin_count_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Тривалість подорожі (днів)").grid(row=2, column=0, sticky="w")
        self.days_entry = tk.Entry(self.root)
        self.days_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Ціна SGL за добу ($)").grid(row=3, column=0, sticky="w")
        self.sgl_price_entry = tk.Entry(self.root)
        self.sgl_price_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Ціна TWIN за добу ($)").grid(row=4, column=0, sticky="w")
        self.twin_price_entry = tk.Entry(self.root)
        self.twin_price_entry.grid(row=4, column=1)

        tk.Label(self.root, text="Додаткові послуги:").grid(row=5, column=0, sticky="w")
        self.services_frame = tk.Frame(self.root)
        self.services_frame.grid(row=6, column=0, columnspan=2, sticky="w")

        self.service_checkboxes = []
        self.service_quantity_entries = []
        self.create_service_checklist()

        tk.Button(self.root, text="Розрахувати", command=self.calculate_cost).grid(row=7, column=0)
        tk.Button(self.root, text="Зберегти розрахунок", command=self.save_calculation).grid(row=7, column=1)
        tk.Button(self.root, text="Відкрити розрахунок", command=self.open_calculation).grid(row=7, column=2)

        self.results_label = tk.Label(self.root, text="", justify="left")
        self.results_label.grid(row=8, column=0, columnspan=3, sticky="w")

    def create_service_checklist(self):
        for service in self.services:
            service_info = (
                f"{service['name']} - {service['type']}, ${service['price']} "
                f"({'за групу' if service['per_group'] == 'за групу' else 'за людину'})"
            )

            var = tk.BooleanVar()
            tk.Checkbutton(self.services_frame, text=service_info, variable=var, anchor="w", justify="left", wraplength=600).pack(anchor="w")
            self.service_checkboxes.append((service, var))
            
            quantity_entry = tk.Entry(self.services_frame, width=5)
            quantity_entry.pack(anchor="w", padx=20)
            self.service_quantity_entries.append((service, quantity_entry))

    def collect_selected_services(self):
        self.selected_services = []
        for (service, var), (_, quantity_entry) in zip(self.service_checkboxes, self.service_quantity_entries):
            if var.get():
                try:
                    quantity = int(quantity_entry.get())
                    if quantity <= 0:
                        raise ValueError
                    self.selected_services.append({**service, "quantity": quantity})
                except ValueError:
                    messagebox.showerror("Помилка", f"Невірна кількість для послуги '{service['name']}'.")
                    return False
        return True

    def calculate_cost(self):
        """Розраховує загальну вартість із поділом на SGL і TWIN."""
        try:
            # Зчитуємо основні дані
            group_size_sgl = int(self.sgl_count_entry.get())
            group_size_twin = int(self.twin_count_entry.get())
            days = int(self.days_entry.get())
            price_sgl = float(self.sgl_price_entry.get())
            price_twin = float(self.twin_price_entry.get())
         
            if not self.collect_selected_services():
                return
         
            rooms_sgl = group_size_sgl  
            rooms_twin = ceil(group_size_twin / 2)  

            total_sgl = rooms_sgl * price_sgl * days
            total_twin = rooms_twin * price_twin * days

            total_people = group_size_sgl + group_size_twin
            
            services_cost = 0
            services_breakdown = []
            for service in self.selected_services:
                if(service["per_group"] == "на людину"):
                    cost = service["price"] * service["quantity"] * total_people
                else:
                    cost = service["price"] * service["quantity"]
                    
                services_cost += cost
                services_breakdown.append(f"- {service['name']}: {service['quantity']} шт., ${cost:.2f}")

            # Загальна вартість
            total_cost = total_sgl + total_twin + services_cost


            cost_per_person_sgl = (
                total_sgl / group_size_sgl + services_cost / total_people if group_size_sgl > 0 else 0
            )
            cost_per_person_twin = (
                total_twin / group_size_twin + services_cost / total_people if group_size_twin > 0 else 0
            )

            # Форматований результат
            result_text = (
                "=== Розрахунок вартості подорожі ===\n\n"
                f"1. Проживання:\n"
                f"   - Номери SGL: {rooms_sgl} шт., ${price_sgl:.2f}/доба, "
                f"Загалом: ${total_sgl:.2f}\n"
                f"   - Номери TWIN: {rooms_twin} шт., ${price_twin:.2f}/доба, "
                f"Загалом: ${total_twin:.2f}\n\n"
                f"2. Додаткові послуги:\n"
                + (("\n".join(services_breakdown) + "\n") if services_breakdown else "   Немає вибраних послуг.\n")
                + f"\nЗагальна вартість послуг: ${services_cost:.2f}\n\n"
                f"=== Підсумок ===\n"
                f"Загальна вартість: ${total_cost:.2f}\n"
                f"Кількість людей: {total_people}\n\n"
                f"=== Вартість на одну людину ===\n"
                f"   - Для SGL: ${cost_per_person_sgl:.2f}\n"
                f"   - Для TWIN: ${cost_per_person_twin:.2f}"
            )

            messagebox.showinfo("Результати розрахунку", result_text)

        except ValueError:
            messagebox.showerror("Помилка", "Будь ласка, введіть коректні числові значення.")

    def save_calculation(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON файли", "*.json")])
        if not file_path:
            return
        data = {
            "sgl_count": self.sgl_count_entry.get(),
            "twin_count": self.twin_count_entry.get(),
            "days": self.days_entry.get(),
            "sgl_price": self.sgl_price_entry.get(),
            "twin_price": self.twin_price_entry.get(),
            "selected_services": self.selected_services
        }
        save_to_json(data, file_path)

    def open_calculation(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON файли", "*.json")])
        if not file_path:
            return
        data = load_from_json(file_path)
        if data:
            self.sgl_count_entry.delete(0, tk.END)
            self.sgl_count_entry.insert(0, data.get("sgl_count", ""))
            self.twin_count_entry.delete(0, tk.END)
            self.twin_count_entry.insert(0, data.get("twin_count", ""))
            self.days_entry.delete(0, tk.END)
            self.days_entry.insert(0, data.get("days", ""))
            self.sgl_price_entry.delete(0, tk.END)
            self.sgl_price_entry.insert(0, data.get("sgl_price", ""))
            self.twin_price_entry.delete(0, tk.END)
            self.twin_price_entry.insert(0, data.get("twin_price", ""))

            for (service, var), (_, quantity_entry) in zip(self.service_checkboxes, self.service_quantity_entries):
                var.set(False)
                quantity_entry.delete(0, tk.END)
            for saved_service in data.get("selected_services", []):
                for (service, var), (_, quantity_entry) in zip(self.service_checkboxes, self.service_quantity_entries):
                    if service["name"] == saved_service["name"]:
                        var.set(True)
                        quantity_entry.insert(0, str(saved_service["quantity"]))
