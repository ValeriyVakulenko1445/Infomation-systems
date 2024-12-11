from datetime import datetime

#Методы для работы с автомобилями, их бронированием

class Car:
    def __init__(self, car_id, brand, model, year, rental_price_per_day):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.year = year
        self.rental_price_per_day = rental_price_per_day
        self.is_available = True

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

class Rental:
    def __init__(self, rental_id, car, customer, start_date, end_date):
        self.rental_id = rental_id
        self.car = car
        self.customer = customer
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = True

    def cancel(self):
        self.is_active = False
        self.car.is_available = True
        print(f"Rental {self.rental_id} canceled.")

class CarRental:
    def __init__(self):
        self.cars = []
        self.rentals = []

    def add_car(self, car):
        self.cars.append(car)
        print(f"Car {car} added to the fleet.")

    def create_rental(self, rental_id, car_id, customer, start_date, end_date):
        car = next((car for car in self.cars if car.car_id == car_id), None)
        if car and car.is_available:
            rental = Rental(rental_id, car, customer, start_date, end_date)
            self.rentals.append(rental)
            car.is_available = False
            print(f"Rental {rental_id} created for {car}.")
        else:
            print("Car not available for rental.")

    def find_available_cars(self, start_date, end_date):
        available_cars = [car for car in self.cars if car.is_available]
        print("Available cars:")
        for car in available_cars:
            print(car)

    def cancel_rental(self, rental_id):
        rental = next((rental for rental in self.rentals if rental.rental_id == rental_id), None)
        if rental and rental.is_active:
            rental.cancel()
        else:
            print("Rental not found or already canceled.")
