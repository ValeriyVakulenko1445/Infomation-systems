import json


class Client:
    def __init__(self, client_id, name, contact, passport_id):
        self.__client_id = client_id
        self.__name = name
        self.__contact = contact
        self.__passport_id = passport_id

    # Геттеры и сеттеры с инкапсуляцией
    @property
    def client_id(self):
        return self.__client_id

    @client_id.setter
    def client_id(self, value):
        self.__client_id = value


    #Статические методы валидации
    @staticmethod
    def validate_contact(contact):
        #Валидация номера телефона
        return isinstance(contact, str) and len(contact) == 10 and contact.isdigit()

    @staticmethod
    def validate_passport_id(passport_id):
        #Проверка номера паспорта
        return isinstance(passport_id, str) and len(passport_id) == 9 and passport_id.isalnum()

    #Прекращение повтора кода в валидации
    def validate_fields(self):
        if not self.validate_contact(self.__contact):
            raise ValueError("Некорректный контакт")
        if not self.validate_passport_id(self.__passport_id):
            raise ValueError("Некорректный номер паспорта")

    # Перегружаем конструктор
    @classmethod
    def from_string(cls, data_str):
        data = json.loads(data_str)
        return cls(**data)

    @classmethod
    def from_json(cls, data_json):
        data = json.loads(data_json)
        return cls(**data)

    #Вывод полной и краткой версии
    def __str__(self):
        return f"Client ID: {self.__client_id}, Name: {self.__name}, Contact: {self.__contact}"

    def short_info(self):
        return f"{self.__name} ({self.__client_id})"

    #Сравнение объектов
    def __eq__(self, other):
        return isinstance(other, Client) and self.__client_id == other.client_id
