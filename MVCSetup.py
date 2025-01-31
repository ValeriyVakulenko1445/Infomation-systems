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

# View (наблюдатель)
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

# Пример запуска
if __name__ == "__main__":
    class MockCarRepository(CarRepBase):
        def __init__(self):
            super().__init__()
            self.cars = [
                {"car_id": 1, "brand": "Toyota", "model": "Camry", "year": 2020, "rental_price_per_day": 50},
                {"car_id": 2, "brand": "Ford", "model": "Focus", "year": 2019, "rental_price_per_day": 40}
            ]
        
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

        def get_count(self):
            return len(self.cars)

    repo = MockCarRepository()
    controller = CarController(repo)
    view = CarView(controller)
