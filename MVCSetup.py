import json
import yaml
import os
import psycopg2
from datetime import datetime
from abc import ABC, abstractmethod

# Паттерн Наблюдатель
class Observer(ABC):
    @abstractmethod
    def update(self):
        pass

class Observable:
    def __init__(self):
        self._observers = []

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update()

# Сущность автомобиля
class Car:
    def __init__(self, car_id, brand, model, year, rental_price_per_day):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.year = year
        self.rental_price_per_day = rental_price_per_day

# Базовый репозиторий
class CarRepBase(Observable, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_by_id(self, car_id):
        pass

    @abstractmethod
    def get_k_n_short_list(self, k, n):
        pass

    @abstractmethod
    def sort_by_field(self, field):
        pass

    @abstractmethod
    def add_car(self, car):
        pass

    @abstractmethod
    def update_car(self, car_id, new_car):
        pass

    @abstractmethod
    def delete_car(self, car_id):
        pass

    @abstractmethod
    def get_count(self):
        pass

# Контроллер для управления логикой
class CarController:
    def __init__(self, repository):
        self.repository = repository

    def get_all_cars(self):
        return self.repository.get_k_n_short_list(100, 0)

    def add_car(self, car):
        self.repository.add_car(car)
        self.repository.notify_observers()

    def update_car(self, car_id, new_car):
        self.repository.update_car(car_id, new_car)
        self.repository.notify_observers()

    def delete_car(self, car_id):
        self.repository.delete_car(car_id)
        self.repository.notify_observers()

    def sort_cars(self, field, reverse=False):
        self.repository.sort_by_field(field, reverse)
        self.repository.notify_observers()

# View
class CarView(Observer):
    def __init__(self, controller):
        self.controller = controller
        self.controller.repository.add_observer(self)
        self.root = tk.Tk()
        self.root.title("Car Rental System")
        self.create_widgets()
        self.update()
        self.root.mainloop()

    def create_widgets(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Brand", "Model", "Year", "Price"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Model", text="Model")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Price", text="Price per day")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.show_car_details)
        
        self.entry_filter = tk.Entry(self.root)
        self.entry_filter.pack()
        
        self.btn_filter = tk.Button(self.root, text="Filter", command=self.apply_filter)
        self.btn_filter.pack()
        
        self.btn_add = tk.Button(self.root, text="Add", command=self.open_add_car_form)
        self.btn_add.pack()
        
        self.btn_delete = tk.Button(self.root, text="Delete", command=self.delete_car)
        self.btn_delete.pack()

        self.btn_sort = tk.Button(self.root, text="Sort by Price", command=lambda: self.sort_cars("rental_price_per_day"))
        self.btn_sort.pack()

    def update(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cars = self.controller.get_all_cars()
        for car in cars:
            self.tree.insert("", tk.END, values=(car['car_id'], car['brand'], car['model'], car['year'], car['rental_price_per_day']))

    def show_car_details(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        car_data = self.tree.item(selected_item, "values")
        messagebox.showinfo("Car Details", f"Brand: {car_data[1]}\nModel: {car_data[2]}\nYear: {car_data[3]}\nPrice per day: {car_data[4]}")
    
    def delete_car(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No car selected")
            return
        car_id = self.tree.item(selected_item, "values")[0]
        self.controller.delete_car(car_id)
        self.update()
    
    def open_add_car_form(self):
        CarFormView(self.root, self.controller)
    
    def apply_filter(self):
        filter_text = self.entry_filter.get().lower()
        filtered_cars = self.controller.filter_cars(lambda car: filter_text in car['brand'].lower() or filter_text in car['model'].lower())
        self.tree.delete(*self.tree.get_children())
        for car in filtered_cars:
            self.tree.insert("", tk.END, values=(car['car_id'], car['brand'], car['model'], car['year'], car['rental_price_per_day']))

    def sort_cars(self, field):
        self.controller.sort_cars(field)
        self.update()

# Форма добавления/редактирования автомобиля
class CarFormView(tk.Toplevel):
    def __init__(self, parent, controller, car=None):
        super().__init__(parent)
        self.controller = controller
        self.car = car
        self.title("Car Form")
        self.create_widgets()
        self.load_car_data()

    def create_widgets(self):
        self.lbl_brand = tk.Label(self, text="Brand")
        self.lbl_brand.pack()
        self.entry_brand = tk.Entry(self)
        self.entry_brand.pack()
        
        self.lbl_model = tk.Label(self, text="Model")
        self.lbl_model.pack()
        self.entry_model = tk.Entry(self)
        self.entry_model.pack()
        
        self.lbl_year = tk.Label(self, text="Year")
        self.lbl_year.pack()
        self.entry_year = tk.Entry(self)
        self.entry_year.pack()
        
        self.lbl_price = tk.Label(self, text="Price per day")
        self.lbl_price.pack()
        self.entry_price = tk.Entry(self)
        self.entry_price.pack()
        
        self.btn_save = tk.Button(self, text="Save", command=self.save_car)
        self.btn_save.pack()

    def load_car_data(self):
        if self.car:
            self.entry_brand.insert(0, self.car['brand'])
            self.entry_model.insert(0, self.car['model'])
            self.entry_year.insert(0, self.car['year'])
            self.entry_price.insert(0, self.car['rental_price_per_day'])
    
    def save_car(self):
        new_car = {
            "brand": self.entry_brand.get(),
            "model": self.entry_model.get(),
            "year": int(self.entry_year.get()),
            "rental_price_per_day": float(self.entry_price.get())
        }
        if self.car:
            self.controller.update_car(self.car['car_id'], new_car)
        else:
            self.controller.add_car(new_car)
        self.destroy()
        
# Пример запуска
if __name__ == "__main__":
    repo = MockCarRepository()
    controller = CarController(repo)
    view = CarView(controller)
