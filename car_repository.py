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

# База
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

# Адаптер для репозиториев
class CarRepositoryAdapter(CarRepBase):
    def __init__(self, repository):
        self.repository = repository

    def get_by_id(self, car_id):
        return self.repository.get_by_id(car_id)

    def get_k_n_short_list(self, k, n):
        return self.repository.get_k_n_short_list(k, n)

    def sort_by_field(self, field):
        return self.repository.sort_by_field(field)

    def add_car(self, car):
        return self.repository.add_car(car)

    def update_car(self, car_id, new_car):
        return self.repository.update_car(car_id, new_car)

    def delete_car(self, car_id):
        return self.repository.delete_car(car_id)

    def get_count(self):
        return self.repository.get_count()

# Декоратор для фильтрации и сортировки
class FilterSortDecorator(CarRepBase):
    def __init__(self, repository, filter_func=None, sort_key=None):
        self.repository = repository
        self.filter_func = filter_func
        self.sort_key = sort_key

    def get_k_n_short_list(self, k, n):
        cars = self.repository.get_k_n_short_list(k, n)
        if self.filter_func:
            cars = list(filter(self.filter_func, cars))
        if self.sort_key:
            cars.sort(key=lambda car: car[self.sort_key])
        return cars

    def get_count(self):
        if self.filter_func:
            return len(list(filter(self.filter_func, self.repository.get_k_n_short_list(1000, 0))))
        return self.repository.get_count()

#JSON
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

# YAML
class CarRepYAML(CarRepBase):
    def __init__(self, filename="cars.yaml"):
        self.filename = filename
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                yaml.dump([], f)

    def read_all(self):
        with open(self.filename, "r") as f:
            return yaml.safe_load(f) or []

    def write_all(self, data):
        with open(self.filename, "w") as f:
            yaml.dump(data, f)

    def get_by_id(self, car_id):
        return next((car for car in self.read_all() if car["car_id"] == car_id), None)

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

#Работа с БД
class CarRepDB(CarRepBase):
    def __init__(self, db_config):
        self.db_config = db_config

    def connect(self):
        return psycopg2.connect(**self.db_config)

    def get_by_id(self, car_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cars WHERE car_id = %s", (car_id,))
                return cur.fetchone()

    def get_k_n_short_list(self, k, n):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cars ORDER BY car_id LIMIT %s OFFSET %s", (k, n * k))
                return cur.fetchall()

    def add_car(self, car):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO cars (brand, model, year, rental_price_per_day) VALUES (%s, %s, %s, %s) RETURNING car_id", 
                            (car.brand, car.model, car.year, car.rental_price_per_day))
                conn.commit()
                return cur.fetchone()[0]

    def update_car(self, car_id, new_car):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE cars SET brand = %s, model = %s, year = %s, rental_price_per_day = %s WHERE car_id = %s", 
                            (new_car.brand, new_car.model, new_car.year, new_car.rental_price_per_day, car_id))
                conn.commit()
                return cur.rowcount > 0

    def delete_car(self, car_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
                conn.commit()

    def get_count(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM cars")
                return cur.fetchone()[0]


# Класс для управления подключением к БД
class DatabaseConnection:
    _instance = None

    def __new__(cls, db_config):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.db_config = db_config
            cls._instance.connection = psycopg2.connect(**db_config)
        return cls._instance

    def get_connection(self):
        return self.connection

# Работа с БД 
class CarRepDB(CarRepBase):
    def __init__(self, db_config):
        self.db_connection = DatabaseConnection(db_config)

    def get_by_id(self, car_id):
        with self.db_connection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cars WHERE car_id = %s", (car_id,))
                return cur.fetchone()

    def add_car(self, car):
        with self.db_connection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO cars (brand, model, year, rental_price_per_day) VALUES (%s, %s, %s, %s) RETURNING car_id", 
                            (car.brand, car.model, car.year, car.rental_price_per_day))
                conn.commit()
                return cur.fetchone()[0]

    def update_car(self, car_id, new_car):
        with self.db_connection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE cars SET brand = %s, model = %s, year = %s, rental_price_per_day = %s WHERE car_id = %s", 
                            (new_car.brand, new_car.model, new_car.year, new_car.rental_price_per_day, car_id))
                conn.commit()
                return cur.rowcount > 0

    def delete_car(self, car_id):
        with self.db_connection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
                conn.commit()

# Декоратор для работы с БД
class FilterSortDBDecorator(CarRepBase):
    def __init__(self, repository, filter_query=None, sort_column=None):
        self.repository = repository
        self.filter_query = filter_query
        self.sort_column = sort_column

    def get_k_n_short_list(self, k, n):
        query = f"SELECT * FROM cars LIMIT {k} OFFSET {n * k}"
        if self.filter_query:
            query = f"SELECT * FROM ({query}) AS filtered WHERE {self.filter_query}"
        if self.sort_column:
            query += f" ORDER BY {self.sort_column}"
        return self.repository.execute_query(query)

    def get_count(self):
        query = "SELECT COUNT(*) FROM cars"
        if self.filter_query:
            query = f"SELECT COUNT(*) FROM (SELECT * FROM cars WHERE {self.filter_query}) AS filtered"
        return self.repository.execute_query(query)[0][0]

# Декоратор для работы с JSON/YAML
class FilterSortFileDecorator(CarRepBase):
    def __init__(self, repository, filter_func=None, sort_key=None):
        self.repository = repository
        self.filter_func = filter_func
        self.sort_key = sort_key

    def get_k_n_short_list(self, k, n):
        cars = self.repository.get_k_n_short_list(k, n)
        if self.filter_func:
            cars = list(filter(self.filter_func, cars))
        if self.sort_key:
            cars.sort(key=lambda car: car[self.sort_key])
        return cars

    def get_count(self):
        if self.filter_func:
            return len(list(filter(self.filter_func, self.repository.get_k_n_short_list(1000, 0))))
        return self.repository.get_count()

