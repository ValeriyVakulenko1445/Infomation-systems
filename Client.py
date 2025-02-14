import re
import json
import yaml
import mysql.connector
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Optional

class Client:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            data = self.parse_json(args[0])
            self.__client_id = data["client_id"]
            self.__full_name = self.validate_and_set("validate_full_name", data["full_name"])
            self.__passport_data = self.validate_and_set("validate_passport_data", data["passport_data"])
            self.__contact_number = self.validate_and_set("validate_contact_number", data["contact_number"])
            self.__address = self.validate_and_set("validate_address", data["address"])
        elif len(args) == 5:
            client_id, full_name, passport_data, contact_number, address = args
            self.__client_id = client_id
            self.__full_name = self.validate_and_set("validate_full_name", full_name)
            self.__passport_data = self.validate_and_set("validate_passport_data", passport_data)
            self.__contact_number = self.validate_and_set("validate_contact_number", contact_number)
            self.__address = self.validate_and_set("validate_address", address)
        else:
            raise ValueError("Invalid arguments for constructor")

    # Геттеры и сеттеры
    def get_client_id(self): 
        return self.__client_id
    def get_full_name(self): 
        return self.__full_name
    def get_passport_data(self): 
        return self.__passport_data
    def get_contact_number(self): 
        return self.__contact_number
    def get_address(self): 
        return self.__address

    def set_full_name(self, full_name: str):
        self.__full_name = self.validate_and_set("validate_full_name", full_name)
    
    # Методы валидации
    @staticmethod
    def validate_full_name(full_name: str) -> bool:
        return bool(full_name) and full_name.replace(" ", "").isalpha()

    @staticmethod
    def validate_passport_data(passport_data: str) -> bool:
        return bool(re.fullmatch(r"\w{10}", passport_data))

    # Остальные методы класса
    def __str__(self):
        return f"Client({self.__client_id}): {self.__full_name}, {self.__contact_number}"

class ClientShort(Client):
    def __init__(self, client: Client):
        super().__init__(
            client.get_client_id(),
            client.get_full_name(),
            "",
            client.get_contact_number(),
            ""
        )
        
    def __str__(self):
        return f"ClientShort({self.get_full_name()}, {self.get_contact_number()})"

class ClientRepository(ABC):
    @abstractmethod
    def read_all(self): 
        pass
    
    @abstractmethod
    def write_all(self, data): 
        pass
    
    @abstractmethod
    def get_by_id(self, client_id): 
        pass
    
    @abstractmethod
    def get_k_n_short_list(self, k: int, n: int): 
        pass
    
    @abstractmethod
    def sort_by_field(self, field: str): 
        pass
    
    @abstractmethod
    def add_client(self, client: Client): 
        pass
    
    @abstractmethod
    def update_client(self, client_id, updated_client: Client): 
        pass
    
    @abstractmethod
    def delete_client(self, client_id): 
        pass
    
    @abstractmethod
    def get_count(self): 
        pass

class ClientRepJson(ClientRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_all(self) -> list:
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def write_all(self, data: list):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def get_by_id(self, client_id: int) -> Optional[Client]:
        data = self.read_all()
        for item in data:
            if item['client_id'] == client_id:
                return Client(**item)
        return None

    def get_k_n_short_list(self, k: int, n: int) -> list[ClientShort]:
        data = self.read_all()[n*k : (n+1)*k]
        return [ClientShort(Client(**item)) for item in data]

    def sort_by_field(self, field: str) -> list:
        data = self.read_all()
        return sorted(data, key=lambda x: x.get(field, ""))

    def add_client(self, client: Client):
        data = self.read_all()
        new_id = max([c['client_id'] for c in data], default=0) + 1
        data.append({
            'client_id': new_id,
            'full_name': client.get_full_name(),
            'passport_data': client.get_passport_data(),
            'contact_number': client.get_contact_number(),
            'address': client.get_address()
        })
        self.write_all(data)

    def update_client(self, client_id: int, updated_client: Client):
        data = self.read_all()
        for item in data:
            if item['client_id'] == client_id:
                item.update({
                    'full_name': updated_client.get_full_name(),
                    'passport_data': updated_client.get_passport_data(),
                    'contact_number': updated_client.get_contact_number(),
                    'address': updated_client.get_address()
                })
                self.write_all(data)
                return
        raise ValueError(f"Client {client_id} not found")

    def delete_client(self, client_id: int):
        data = [c for c in self.read_all() if c['client_id'] != client_id]
        self.write_all(data)

    def get_count(self) -> int:
        return len(self.read_all())

class ClientRepYaml(ClientRepJson):
    def read_all(self) -> list:
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f) or []
        except (FileNotFoundError, yaml.YAMLError):
            return []

    def write_all(self, data: list):
        with open(self.file_path, 'w') as f:
            yaml.dump(data, f)

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password",
                database="car_rental"
            )
        return cls._instance
    
    def get_connection(self):
        return self.connection

class ClientRepDB(ClientRepository):
    def __init__(self):
        self.db = DatabaseConnection().get_connection()

    def get_by_id(self, client_id: int) -> Optional[Client]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients WHERE client_id = %s", (client_id,))
        result = cursor.fetchone()
        cursor.close()
        return Client(**result) if result else None

    def get_k_n_short_list(self, k: int, n: int) -> list[ClientShort]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients LIMIT %s OFFSET %s", (k, n*k))
        results = cursor.fetchall()
        cursor.close()
        return [ClientShort(Client(**item)) for item in results]

    def add_client(self, client: Client):
        cursor = self.db.cursor()
        cursor.execute(
            """INSERT INTO clients 
            (full_name, passport_data, contact_number, address) 
            VALUES (%s, %s, %s, %s)""",
            (client.get_full_name(), client.get_passport_data(),
             client.get_contact_number(), client.get_address())
        )
        self.db.commit()
        cursor.close()

    def update_client(self, client_id: int, updated_client: Client):
        cursor = self.db.cursor()
        cursor.execute(
            """UPDATE clients SET 
            full_name = %s, passport_data = %s, 
            contact_number = %s, address = %s 
            WHERE client_id = %s""",
            (updated_client.get_full_name(), updated_client.get_passport_data(),
             updated_client.get_contact_number(), updated_client.get_address(),
             client_id)
        )
        self.db.commit()
        cursor.close()

    def delete_client(self, client_id: int):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))
        self.db.commit()
        cursor.close()

    def get_count(self) -> int:
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        cursor.close()
        return count

class ClientDBAdapter(ClientRepDB):
    def read_all(self):
        raise NotImplementedError("Direct read_all not supported for DB")
    
    def write_all(self, data):
        raise NotImplementedError("Direct write_all not supported for DB")
    
    def sort_by_field(self, field: str):
        raise NotImplementedError("Use SQL ORDER BY instead")

class FilterSortDecorator(ClientRepository):
    def __init__(self, repository: ClientRepository, 
                 filter_func: Callable = None, 
                 sort_key: Callable = None):
        self.repository = repository
        self.filter_func = filter_func
        self.sort_key = sort_key

    def get_k_n_short_list(self, k: int, n: int) -> list[ClientShort]:
        data = self.repository.get_k_n_short_list(k, n)
        if self.filter_func:
            data = list(filter(self.filter_func, data))
        if self.sort_key:
            data.sort(key=self.sort_key)
        return data

    def get_count(self) -> int:
        if self.filter_func:
            return len(list(filter(self.filter_func, 
                                self.repository.get_k_n_short_list(1000, 0))))
        return self.repository.get_count()

    def __getattr__(self, name):
        return getattr(self.repository, name)

# Пример использования
if __name__ == "__main__":
    # Инициализация репозиториев
    json_repo = ClientRepJson("clients.json")
    yaml_repo = ClientRepYaml("clients.yaml")
    db_repo = ClientDBAdapter()
    
    # Пример с декоратором
    filtered_db_repo = FilterSortDecorator(
        db_repo,
        filter_func=lambda c: "Иванов" in c.get_full_name(),
        sort_key=lambda c: c.get_contact_number()
    )
    
    # Получение данных
    print("Первые 10 клиентов из DB:", filtered_db_repo.get_k_n_short_list(10, 0))
    print("Всего клиентов в JSON:", json_repo.get_count())
