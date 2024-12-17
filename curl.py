import random
import subprocess
import time
import urllib.parse
import json
import sys
import logging



# Проверка аргументов командной строки
if len(sys.argv) < 3:
    print("Usage: python curl.py <filename>")
    sys.exit(1)

# Получение имени файла из аргументов командной строки
filename = sys.argv[1]
logFile = "logs/" + filename + ".log"

# Настройка логирования
logging.basicConfig(
    filename=logFile,       # Имя лог-файла
    level=logging.DEBUG,          # Уровень логирования (можно использовать DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат записи в лог
)

file_path = "json/" + filename + ".json"

logging.info('Чтение из файла ' + file_path)
# Чтение данных JSON из файла
try:
    with open(file_path, "r", encoding="utf-8") as file:
        clients = json.load(file)
except FileNotFoundError:
    logging.error(f"Файл не найден: {file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    logging.error(f"Ошибка чтения JSON из файла: {file_path}")
    sys.exit(1)


#Получаем количество записей
amount = filename = sys.argv[2]

# Проверка размера массива JSON
if len(clients) < int(amount):
    logging.error(f"Ошибка: Размер массива JSON ({len(clients)}) меньше {amount} записей.")
    sys.exit(1)
else:
    logging.debug("Количество записей соответствует размеру массива")

# API ключ и URL
API_KEY = "<email-engine-key>"
API_URL = "<email-engine-url>"

# Константы для задержки
LONG_DELAY_MIN = 4 * 60 + 12  # Минимальная долгая задержка 4 минуты и 12 секунд в секундах
LONG_DELAY_MAX = 7 * 60 + 57  # Максимальная долгая задержка 7 минут и 57 секунд в секундах
RANDOM_DELAY_MIN = 20  # Минимальная случайная задержка
RANDOM_DELAY_MAX = 100  # Максимальная случайная задержка

# Счётчик итераций
iteration_count = 0

# Общие параметры для всех запросов
list_ids = "15,134"
double_optin = 0
overwrite = 0

# Функция для отправки данных клиента через curl
for client in clients:
    # Обязательное поле email
    email = client.get("email")
    if not email:
        logging.debug("Пропущен клиент без email:", client)
        continue

    # Опциональные поля
    client_tariff = client.get("client_tariff", "")
    client_name = client.get("client_name", "")
    client_type = client.get("client_type", "")
    client_sex = client.get("client_sex", "")
    industry = client.get('client_company_type', "")
    client_firstname = client.get("client_firstname", "")
    client_lastname = client.get("client_lastname", "")
    manager = client.get("manager_name", "")
    client_department = client.get('client_company_department', "")

    phone = client.get("phone", "")


    # Параметры запроса
    params = {
        "format": "json",
        "api_key": API_KEY,
        "list_ids": list_ids,
        "fields[email]": email,
        "fields[phone]": phone,
        "fields[CustomerCustomFieldsClientType]": client_type,
        "fields[CustomerCustomFieldsCompanyName]": client_name,
        "fields[CustomerSex]": client_sex,
        "fields[CustomerCustomFieldsManagerDepartment]": client_department,
        "fields[CustomerCustomFieldsManagerName]": manager,
        "fields[CustomerCustomFieldsClientTariff]": client_tariff,
        "fields[Name]": client_firstname,
        "fields[last_name]": client_lastname,
        "fields[industry]": industry,
        "double_optin": double_optin,
        "overwrite": overwrite
    }


    # Преобразование параметров в строку для curl
    query_string = urllib.parse.urlencode(params)
    curl_command = [
        "curl",
        "-X", "POST",
        f"{API_URL}?{query_string}"
    ]


    # Выполнение команды curl
    try:
        result = subprocess.run(curl_command, check=True, text=True, capture_output=True)
        logging.info(f"Успешно отправлено для {email}: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при отправке для {email}: {e.stderr}")

    # Увеличиваем счётчик итераций
    iteration_count += 1

    # Проверяем, нужно ли сделать длительную задержку
    if iteration_count % 87 == 0:
        delay_time = random.randint(LONG_DELAY_MIN, LONG_DELAY_MAX)
        logging.debug(f"Итерация {iteration_count}: Задержка на {delay_time}.")
        time.sleep(delay_time)  # Длительная задержка
    else:
        delay_time = random.randint(RANDOM_DELAY_MIN, RANDOM_DELAY_MAX)
        logging.debug(f"Итерация {iteration_count}: Задержка на {delay_time} секунд.")
        time.sleep(delay_time)  # Случайная задержка от 20 до 100 секунд
