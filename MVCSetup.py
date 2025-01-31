import tkinter as tk
from tkinter import ttk

# Интерфейс Наблюдателя
class Observer:
    def update(self):
        pass

# Модель с поддержкой Наблюдателя
class CarModel:
    def __init__(self, repository):
        self.repository = repository
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update()

    def get_cars(self):
        return self.repository.get_k_n_short_list(10, 0)

# Представление (GUI)
class CarView(tk.Tk, Observer):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Car Rental")
        self.geometry("600x400")

        self.tree = ttk.Treeview(self, columns=("ID", "Brand", "Model", "Year"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Model", text="Model")
        self.tree.heading("Year", text="Year")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.controller.model.add_observer(self)
        self.update()

    def update(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        cars = self.controller.get_cars()
        for car in cars:
            self.tree.insert("", "end", values=(car["car_id"], car["brand"], car["model"], car["year"]))

# Контроллер
class CarController:
    def __init__(self, repository):
        self.model = CarModel(repository)
        self.view = CarView(self)
    
    def get_cars(self):
        return self.model.get_cars()

    def run(self):
        self.view.mainloop()

# Подключение репозитория (заглушка, вместо репозитория можно передать реальный)
class MockRepository:
    def get_k_n_short_list(self, k, n):
        return [{"car_id": i, "brand": "Brand"+str(i), "model": "Model"+str(i), "year": 2000+i} for i in range(k)]

# Запуск приложения
if __name__ == "__main__":
    repository = MockRepository()
    controller = CarController(repository)
    controller.run()
