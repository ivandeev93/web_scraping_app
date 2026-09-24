import requests
from bs4 import BeautifulSoup
import csv


# Создание файла таблицы и его шапки
with open('auto.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow([
        'Наименование', 'Начальная цена', 'Максимальная цена',
        'Тип двигателя', 'Объём двигателя', 'Мощность двигателя',
        'Коробка передач', 'Тип привода', 'Количество комплектаций'])



for i in range(1, 19):
    # Объявление сессии запроса
    with requests.Session() as session:
        response = session.get(url=f'https://kolesa.kz/cars/new/?page={i}')
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

        for i in price:
            parts = i.split('—')

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


## Возможные улучшения

#В дальнейшем проект можно расширить:

#* добавить `requirements.txt`
#* добавить обработку ошибок HTTP-запросов
#* использовать одну `Session` для всех страниц
#* добавить задержку между запросами
#* добавить логирование
#* сделать количество страниц параметром командной строки
#* добавить сохранение в JSON
#* добавить обработку дубликатов
#* использовать Pandas для дальнейшего анализа
#* добавить Docker
#* добавить автоматический запуск через GitHub Actions