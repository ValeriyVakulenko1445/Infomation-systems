import re
import json


class Client:
    def __init__(self, client_id: int, full_name: str, passport_data: str, contact_number: str, address: str):
        self.__client_id = client_id
        self.__full_name = self.validate_full_name(full_name)
        self.__passport_data = self.validate_passport_data(passport_data)
        self.__contact_number = self.validate_contact_number(contact_number)
        self.__address = self.validate_address(address)

    @classmethod
    def from_json(cls, json_str: str):
        #Альтернативный конструктор для создания объекта из JSON
        data = json.loads(json_str)
        return cls(
            data["client_id"],
            data["full_name"],
            data["passport_data"],
            data["contact_number"],
            data["address"]
        )

    # Геттеры
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

    # Сеттеры
    def set_full_name(self, full_name: str):
        self.__full_name = self.validate_full_name(full_name)

    def set_passport_data(self, passport_data: str):
        self.__passport_data = self.validate_passport_data(passport_data)

    def set_contact_number(self, contact_number: str):
        self.__contact_number = self.validate_contact_number(contact_number)

    def set_address(self, address: str):
        self.__address = self.validate_address(address)

    # Методы валидации
        """Методы валидации возвращают валидированное значение str вместо bool, так как проще сразу использовать корректные данные без дополнительной обработки."""
    @staticmethod
    def validate_full_name(full_name: str) -> str:
        if full_name and full_name.replace(" ", "").isalpha():
            return full_name
        raise ValueError(f"Invalid full name: {full_name}")

    @staticmethod
    def validate_passport_data(passport_data: str) -> str:
        if re.fullmatch(r"\d{10}", passport_data):
            return passport_data
        raise ValueError(f"Invalid passport data: {passport_data}")

    @staticmethod
    def validate_contact_number(contact_number: str) -> str:
        if re.fullmatch(r"^\+?\d{10,15}$", contact_number):
            return contact_number
        raise ValueError(f"Invalid contact number: {contact_number}")

    @staticmethod
    def validate_address(address: str) -> str:
        if address.strip():
            return address
        raise ValueError(f"Invalid address: {address}")

    # Методы строкового представления
    def full_string(self):
        return (f"Client({self.__client_id}): {self.__full_name}, "
                f"Passport: {self.__passport_data}, Contact: {self.__contact_number}, Address: {self.__address}")

    def short_string(self):
        return f"ClientShort({self.__full_name}, {self.__contact_number})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Client):
            return self.__client_id == other.__client_id
        return False


class ClientShort:
    """Краткая информация о клиенте"""
    def __init__(self, client: Client):
        self.__client = client 

    def get_full_name(self):
        return self.__client.get_full_name()

    def get_contact_number(self):
        return self.__client.get_contact_number()

    def full_string(self):
        return f"ClientShort({self.get_full_name()}, {self.get_contact_number()})"


class ClientRepository(ABC):
    @abstractmethod
    def read_all(self):  # Получаем полный список клиентов
        pass
    
    @abstractmethod
    def write_all(self, data): # Запись списка клиентов в хранилище
        pass
    
    @abstractmethod
    def get_by_id(self, client_id): # Поиск по client_id, возвращает объект, если не найдет вернет None
        pass
    
    @abstractmethod
    def get_k_n_short_list(self, k: int, n: int): # Считывает данные, возвращает список клиентов(берется к записей начиная с n*к)
        pass
    
    @abstractmethod
    def sort_by_field(self, field: str): # Сортировка по указанному полю, возвращает уже отсортированный список
        pass
    
    @abstractmethod
    def add_client(self, client: Client): # Добавление нового клиента
        pass
    
    @abstractmethod
    def update_client(self, client_id, updated_client: Client): # Обновление информации о клиенте
        pass
    
    @abstractmethod
    def delete_client(self, client_id): # Удаление клиента по id
        pass
    
    @abstractmethod
    def get_count(self): # Подсчет кол-ва клиентов (возвращает количество клиентов)
        pass

class ClientRepJson(ClientRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path
        
# Чтение JSON-файла. Если файл пустой или его нету, возвращает пустой список 
    def read_all(self) -> list:
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
            
# Запись списка клиентов в JSON-файл( с отступами)
    def write_all(self, data: list):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
            
#Чтение данных. Ищет клиента по client_id, если нашел, возвращает объект, иначе возвращает None
    def get_by_id(self, client_id: int) -> Optional[Client]:
        data = self.read_all()
        for item in data:
            if item['client_id'] == client_id:
                return Client(**item)
        return None
        
# Возвращает список клиентов. Берется k записей, начиная с n*k
    def get_k_n_short_list(self, k: int, n: int) -> list[ClientShort]:
        data = self.read_all()[n*k : (n+1)*k]
        return [ClientShort(Client(**item)) for item in data]
        
# Сортирует по field. Возвращает отсортированный список
    def sort_by_field(self, field: str) -> list:
        data = self.read_all()
        return sorted(data, key=lambda x: x.get(field, ""))
        
# Определение нового client_id, который будет на 1 больше максимального. Добавляет клиента и записывает обратно
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
        
# Обновляет информацию о клиенте, если он найден. Записывает обновленные данные
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
        
# Удаление клиента. Записывает обновленный список
    def delete_client(self, client_id: int):
        data = [c for c in self.read_all() if c['client_id'] != client_id]
        self.write_all(data)
        
# Возвращает количество клиентов
    def get_count(self) -> int:
        return len(self.read_all())
# Данный Класс наследуется от ClientRepJson, но тут заменяются методы: "read_all" и "write_all", чтобы можно было работать с YAML.
class ClientRepYaml(ClientRepJson):
# Аналогично с JSON
    def read_all(self) -> list:
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f) or []
        except (FileNotFoundError, yaml.YAMLError):
            return []

# Аналогично с JSON
    def write_all(self, data: list):
        with open(self.file_path, 'w') as f:
            yaml.dump(data, f)

# Класс подключения к Базе данных, используется паттерн Одиночка (гарантирует что будет ТОЛЬКО одно подключение к БД)
class DatabaseConnection:
    
    _instance = None # Статическая переменная, которая будет хранить единственный экземпляр класса

# Метод отвечает за создание экземпляра класса, в нем реализована проверка Если cls._instance == None, создаем объект и устанавливаем соединение с MySQL, если же объект уже существует, просто вернет его.
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls) # super - функция, которая позволяет вызвать метоы родительского класса
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
    
#Подключение к базе, через DatabaseConnection
    def __init__(self):
        self.db = DatabaseConnection().get_connection()

# Выполняет SQL-запрос SELECT * FROM clients WHERE client_id = %s, если найден, создает Client
    def get_by_id(self, client_id: int) -> Optional[Client]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients WHERE client_id = %s", (client_id,))
        result = cursor.fetchone()
        cursor.close()
        return Client(**result) if result else None
        
# Запрашивает k записей с OFFSET n*k
    def get_k_n_short_list(self, k: int, n: int) -> list[ClientShort]:
        cursor = self.db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients LIMIT %s OFFSET %s", (k, n*k))
        results = cursor.fetchall()
        cursor.close()
        return [ClientShort(Client(**item)) for item in results]

# Выполняет INSERT INTO clients (Добавление клиента)
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

# Выполняет UPDATE clients SET ... WHERE client_id = %s
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
        
# Выполняет DELETE FROM clients WHERE client_id = %s
    def delete_client(self, client_id: int):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))
        self.db.commit()
        cursor.close()

# Выполняет SELECT COUNT(*) FROM clients (Возврат кол-ва клиентов)
    def get_count(self) -> int:
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        count = cursor.fetchone()[0]
        cursor.close()
        return count


class ClientDBAdapter(ClientRepDB): # Адаптер для ClientRepDB, который запрещает read_all() и write_all(), так как БД использует SQL-запросы
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
# Данные методы реализуют паттерн "Декоратор", для того чтобы реализовать фильтрацию и сортировку у ClientRepository
    def get_k_n_short_list(self, k: int, n: int) -> list[ClientShort]:
        data = self.repository.get_k_n_short_list(k, n) # Получаем
        if self.filter_func:
            data = list(filter(self.filter_func, data)) # Фильтруем данные
        if self.sort_key:
            data.sort(key=self.sort_key) # Сортируем данные
        return data # Возвращаем результат
        
        # Метод возвращает количество клиентов, учитывая фильтрацию
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
