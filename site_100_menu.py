import random
import json
import csv
from time import sleep

import requests
from bs4 import BeautifulSoup

"""
Парсер сайта https://1000.menu/
В результате получаем в разрезе групп продуктов по три файла: 
    - страница сайт с группой продуктов,
    - файл с таблицей продуктов и информацией о калорийности, содержание углеводов, белков и жиров, а также гликемический индекс,
    - файл в формате json с аналогичной информацией
    
    Для удобства код частично закомментирован. 
    Для работы самого парсера достаточно запустить не закомментированный код. Если есть необходимость можно запустить 
    поэтапно с сохранением промежуточных файлов - запуск блоков по номеру в комментариях 
"""


# url = "https://1000.menu/food-table"
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# 1. записываем стартовую страницу в файл для дальнейшей работы с ней
# req = requests.get(url, headers=headers)
# src = req.text
#
# with open("index.html", "w", encoding="UTF-8") as file:
#     file.write(src)

# 2. работаем с сохраненным файлом, чтобы частые обращения к странице на заблокировали нас
# with open("index.html", "r", encoding="UTF-8") as file:
#     src = file.read()

# создаем словарь всех категорий продуктов и записываем их в файл json
# soup = BeautifulSoup(src, "lxml")
# base_url = "https://1000.menu"
# all_groups_dict = {}
#
# all_group_products = soup.find_all("div", class_="name")
# for group in all_group_products:
#     name_group = group.find("a").text
#     href_group = base_url + group.find("a").get('href')
#
#     all_groups_dict[name_group] = href_group
#
# with open("all_group_products.json", "w") as file:
#     json.dump(all_groups_dict, file, indent=4, ensure_ascii=False)

# 3. работаем со словарем и создаем отдельные файлы групп
with open("all_group_products.json") as file:
    all_groups = json.load(file)

index = 0
iteration_count = int(len(all_groups)) - 1
print(f'Всего итераций: {iteration_count}')

for group_name, group_href in all_groups.items():

    rep = [", ", " "]
    for item in rep:
        if item in group_name:
            group_name = group_name.replace(item, "_")

    req = requests.get(url=group_href, headers=headers)
    src = req.text

    with open(f"data/{index}_{group_name}.html", "w", encoding="UTF-8") as file:
        file.write(src)

    with open(f"data/{index}_{group_name}.html", encoding="UTF-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # собираем заголовки таблицы
    table_head = soup.find('table', id="food-table").find_all('th')
    product = table_head[0].text.strip()
    proteins = table_head[1].text.strip()
    fats = table_head[2].text.strip()
    carbohydrates = table_head[3].text.strip()
    calories = table_head[4].text.strip()
    gi = table_head[5].text.strip()

    with open(f"data/{index}_{group_name}.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                product,
                proteins,
                fats,
                carbohydrates,
                calories,
                gi
            )
        )

    # собираем строки таблицы - данные по продуктам
    data_products_table = soup.find('table', id="food-table").find_all('tr')

    product_info = []

    for row in data_products_table[1:]:
        data_row = row.find_all("td")
        name = data_row[0].text
        proteins = data_row[1].text
        fats = data_row[2].text
        carbohydrates = data_row[3].text
        calories = data_row[4].text
        gi = data_row[5].text

        product_info.append(
            {
                "title": name,
                "proteins": proteins,
                "fats": fats,
                "carbohydrates": carbohydrates,
                "calories": calories,
                "gi": gi
            }
        )

        with open(f"data/{index}_{group_name}.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    name,
                    proteins,
                    fats,
                    carbohydrates,
                    calories,
                    gi
                )
            )

    with open(f"data/{index}_{group_name}.json", 'a', encoding="utf-8") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    print(f"#Итерация {index}. Группа продуктов '{group_name}' записана...")
    index += 1
    iteration_count -= 1

    if iteration_count == 0:
        print("Работа закончена")
        break

    print(f"Осталось итераций {iteration_count}")
    sleep(random.randrange(2, 4))
