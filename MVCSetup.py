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

# Контроллер для окна добавления автомобиля
class AddCarController:
    def __init__(self, repository, parent_view):
        self.repository = repository
        self.parent_view = parent_view

    def add_car(self, brand, model, year, price):
        if not brand or not model or not year.isdigit() or not price.replace('.', '', 1).isdigit():
            messagebox.showerror("Ошибка", "Некорректные данные")
            return
        new_id = max([car['car_id'] for car in self.repository.cars], default=0) + 1
        new_car = {"car_id": new_id, "brand": brand, "model": model, "year": int(year), "rental_price_per_day": float(price)}
        self.repository.add_car(new_car)
        self.parent_view.update()

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
        
        self.add_button = tk.Button(self.root, text="Добавить", command=self.open_add_window)
        self.add_button.pack()

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
    
    def open_add_window(self):
        AddCarView(self.controller.repository, self)

# Окно добавления автомобиля
class AddCarView:
    def __init__(self, repository, parent_view):
        self.controller = AddCarController(repository, parent_view)
        self.window = tk.Toplevel()
        self.window.title("Добавить автомобиль")

        tk.Label(self.window, text="Brand:").pack()
        self.brand_entry = tk.Entry(self.window)
        self.brand_entry.pack()

        tk.Label(self.window, text="Model:").pack()
        self.model_entry = tk.Entry(self.window)
        self.model_entry.pack()

        tk.Label(self.window, text="Year:").pack()
        self.year_entry = tk.Entry(self.window)
        self.year_entry.pack()

        tk.Label(self.window, text="Price per day:").pack()
        self.price_entry = tk.Entry(self.window)
        self.price_entry.pack()

        tk.Button(self.window, text="Добавить", command=self.add_car).pack()

    def add_car(self):
        self.controller.add_car(self.brand_entry.get(), self.model_entry.get(), self.year_entry.get(), self.price_entry.get())
        self.window.destroy()

# Пример запуска
if __name__ == "__main__":
    class MockCarRepository(CarRepBase):
        def __init__(self):
            super().__init__()
            self.cars = []
        
        def get_by_id(self, car_id):
            return next((car for car in self.cars if car["car_id"] == car_id), None)

        def get_k_n_short_list(self, k, n):
            return self.cars[n*k:(n+1)*k]

        def sort_by_field(self, field):
            self.cars.sort(key=lambda x: x[field])

        def add_car(self, car):
            self.cars.append(car)
            self.notify_observers()

        def update_car(self, car_id, new_car):
            for idx, car in enumerate(self.cars):
                if car["car_id"] == car_id:
                    self.cars[idx] = new_car
                    self.notify_observers()
                    break

        def delete_car(self, car_id):
            self.cars = [car for car in self.cars if car["car_id"] != car_id]
            self.notify_observers()

    repo = MockCarRepository()
    controller = CarController(repo)
    view = CarView(controller)
