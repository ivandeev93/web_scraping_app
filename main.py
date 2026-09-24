import requests
from bs4 import BeautifulSoup
import csv
import time
from fake_useragent import UserAgent



# Создание объекта для генерации User-Agent
ua = UserAgent()

# Подготовка прокси
#proxies = {
#    'http': 'http://200.12.55.90:80',
#    'https': 'http://200.12.55.90:80'
#}

# Подготовка заголовков
headers = {"User-Agent": ua.random}


# Создание файла таблицы и его шапки
with open('auto.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow([
        'Наименование', 'Начальная цена', 'Максимальная цена',
        'Тип двигателя', 'Объём двигателя', 'Мощность двигателя',
        'Коробка передач', 'Тип привода', 'Количество комплектаций'])


# Объявление сессии запроса
with requests.Session() as session:
    # Нахождение количества страниц
    response = session.get("https://kolesa.kz/cars/new/",
                           headers=headers,
                           #proxies=proxies,
                           timeout=10
                           )

    response.encoding = 'utf-8'
    data = response.text
    soup = BeautifulSoup(data, 'html.parser')
    last_li = soup.select_one(".pager ul li:last-child")
    pages = int(last_li.get_text(strip=True))

    # Обход страниц сайта
    for i in range(1, pages + 1):
        try:
            response = session.get(
                f'https://kolesa.kz/cars/new/',
                params={"page": i},
                headers=headers,
                #proxies=proxies,
                timeout=10
            )
            response.raise_for_status()

            print(response.status_code)

            response.encoding = 'utf-8'
            data = response.text

            soup = BeautifulSoup(data, 'html.parser')

            # Набор составных частей данных
            cards = soup.find_all('div', class_="model-card__heading")
            names = [i.find('h5', class_='model-card__title').text.strip() for i in cards]
            price = [i.get_text(' ', strip=True) for i in soup.find_all('p', class_='model-card__price')]

            # Сбор начальных и максимальных цен со страницы
            start_price = []
            max_price = []

            for p in price:
                parts = p.split('—')

                start_price.append(parts[0].replace('₸', '').strip())

                if len(parts) > 1:
                    max_price.append(parts[1].replace('₸', '').strip())
                else:
                    max_price.append(parts[0].replace('₸', '').strip())

            description = [i.text.strip().split('\n') for i in soup.find_all('ul', class_='model-card__features')]

            with open('auto.csv', 'a', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file, delimiter=';')
                for name, start_price, max_price, descr in zip(names, start_price, max_price, description):
                    # Формируем строку для записи
                    if descr[0] == 'Электричество':
                        descr.insert(1, '')
                    flatten = name, start_price, max_price, *[x for x in descr]
                    writer.writerow(flatten)

            time.sleep(2)

        except requests.exceptions.ConnectTimeout:
            print("Не удалось подключиться к kolesa.kz: превышено время ожидания")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")

        except requests.exceptions.ProxyError as e:
            print(f"Ошибка прокси: {e}")

## Возможные улучшения

#В дальнейшем проект можно расширить:

#* добавить обработку ошибок HTTP-запросов
#* добавить задержку между запросами
#* добавить логирование
#* сделать количество страниц параметром командной строки
#* добавить сохранение в JSON
#* добавить обработку дубликатов
#* добавить Docker
#* добавить автоматический запуск через GitHub Actions