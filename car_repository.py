import json
import yaml
import os
from datetime import datetime

# Сущность автомобиля
class Car:
    def __init__(self, car_id, brand, model, year, rental_price_per_day):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.year = year
        self.rental_price_per_day = rental_price_per_day

# Базовый репозиторий
class CarRepBase:
    def get_by_id(self, car_id):
        raise NotImplementedError

    def get_k_n_short_list(self, k, n):
        raise NotImplementedError

    def sort_by_field(self, field):
        raise NotImplementedError

    def add_car(self, car):
        raise NotImplementedError

    def update_car(self, car_id, new_car):
        raise NotImplementedError

    def delete_car(self, car_id):
        raise NotImplementedError

    def get_count(self):
        raise NotImplementedError

# Репозиторий JSON
class CarRepJSON(CarRepBase):
    def __init__(self, filename="cars.json"):
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump([], f)

    def read_all(self):
        with open(self.filename, "r") as f:
            return json.load(f)

    def write_all(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

    def get_by_id(self, car_id):
        return next((car for car in self.read_all() if car["car_id"] == car_id), None)

    def get_k_n_short_list(self, k, n):
        data = self.read_all()
        return data[n * k:(n + 1) * k]

    def sort_by_field(self, field):
        data = self.read_all()
        data.sort(key=lambda x: x[field])
        self.write_all(data)

    def add_car(self, car):
        data = self.read_all()
        car.car_id = max([c["car_id"] for c in data], default=0) + 1
        data.append(car.__dict__)
        self.write_all(data)

    def update_car(self, car_id, new_car):
        data = self.read_all()
        for i, car in enumerate(data):
            if car["car_id"] == car_id:
                data[i] = new_car.__dict__
                self.write_all(data)
                return True
        return False

    def delete_car(self, car_id):
        data = self.read_all()
        data = [car for car in data if car["car_id"] != car_id]
        self.write_all(data)

    def get_count(self):
        return len(self.read_all())
