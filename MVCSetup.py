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

    def update(self):
        print("Данные обновлены. Перерисовываем интерфейс.")
        self.display_cars()

    def display_cars(self):
        cars = self.controller.get_all_cars()
        for car in cars:
            print(f"{car['car_id']}: {car['brand']} {car['model']} - {car['rental_price_per_day']} руб/день")
