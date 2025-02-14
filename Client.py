import re
import json
import yaml
import mysql.connector
from abc import ABC, abstractmethod

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

    def set_passport_data(self, passport_data: str):
        self.__passport_data = self.validate_and_set("validate_passport_data", passport_data)

    def set_contact_number(self, contact_number: str):
        self.__contact_number = self.validate_and_set("validate_contact_number", contact_number)

    def set_address(self, address: str):
        self.__address = self.validate_and_set("validate_address", address) 

    @staticmethod
    def validate_and_set(validation_method: str, value: str):
        validator = getattr(Client, validation_method, None)
        if not validator or not validator(value):
            raise ValueError(f"Invalid value for {validation_method.replace('validate_', '')}")
        return value

    @staticmethod
    def validate_full_name(full_name: str) -> bool:
        return bool(full_name) and full_name.replace(" ", "").isalpha()

    @staticmethod
    def validate_passport_data(passport_data: str) -> bool:
        return bool(re.fullmatch(r"\w{10}", passport_data))

    @staticmethod
    def validate_contact_number(contact_number: str) -> bool:
        return bool(re.fullmatch(r"\+?\d{10,15}", contact_number))

    @staticmethod
    def validate_address(address: str) -> bool:
        return bool(address)

    @staticmethod
    def parse_json(json_string: str) -> dict:
        try:
            data = json.loads(json_string)
            required_keys = {"client_id", "full_name", "passport_data", "contact_number", "address"}
            if not required_keys.issubset(data.keys()):
                raise ValueError("Missing required keys in JSON data")
            return data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")

    def __str__(self):
        return f"Client({self.__client_id}): {self.__full_name}, {self.__contact_number}"

    def __eq__(self, other):
        if isinstance(other, Client):
            return self.__client_id == other.__client_id
        return False

class ClientShort(Client):
    def __init__(self, client: Client):
        self.__client_id = client.get_client_id()
        self.__full_name = client.get_full_name()
        self.__contact_number = client.get_contact_number()

    def __str__(self):
        return f"ClientShort({self.__full_name}, {self.__contact_number})"

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
    def get_count(self):
        pass

class ClientRepJson(ClientRepository):
    def __init__(self, file_path):
        self.file_path = file_path

    def read_all(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def write_all(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def get_by_id(self, client_id):
        data = self.read_all()
        for item in data:
            if item['client_id'] == client_id:
                return Client(**item)
        return None

    def get_count(self):
        return len(self.read_all())

class ClientRepYaml(ClientRepository):
    def __init__(self, file_path):
        self.file_path = file_path

    def read_all(self):
        with open(self.file_path, 'r') as file:
            return yaml.safe_load(file)

    def write_all(self, data):
        with open(self.file_path, 'w') as file:
            yaml.dump(data, file)

    def get_by_id(self, client_id):
        data = self.read_all()
        for item in data:
            if item['client_id'] == client_id:
                return Client(**item)
        return None

    def get_count(self):
        return len(self.read_all())

class DatabaseConnection:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = mysql.connector.connect(
                host="localhost", user="root", password="password", database="car_rental"
            )
        return cls._instance

    def get_connection(self):
        return self.connection
