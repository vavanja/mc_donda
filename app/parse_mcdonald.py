import requests
import json
import re
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC


def parse():
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    url = 'https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html'
    response = requests.get(url)
    webpage = response.text
    soup = BeautifulSoup(webpage, 'html.parser')
    menu_items = soup.find_all('li', class_='cmp-category__item')
    products_list = []

    for item in menu_items:
        product_url = item.find('a', {'data-cmp-clickable': ''})
        data_layer = json.loads(product_url['data-cmp-data-layer'])
        link_url = data_layer.get(list(data_layer.keys())[0], {}).get('xdm:linkURL', '')
        products_list.append(f"https://www.mcdonalds.com{link_url}")

    data_to_write = []
    for url in products_list:
        driver.get(url)

        time.sleep(0.5)
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'cmp-accordion__button'))
        )
        button.click()
        product_name = driver.find_element(By.CLASS_NAME, 'cmp-product-details-main__desktop-only')
        product_description = driver.find_element(By.CLASS_NAME, 'cmp-product-details-main__description')
        product_name = product_name.text.split("\n")[0]
        element = driver.find_element(By.ID, 'pdp-nutrition-summary')
        parsed_data = extract_data(element.text, name=product_name, description=product_description.text)
        data_to_write.append(parsed_data)

    with open('app/menu.json', 'w', encoding='utf-8') as file:
        json.dump(data_to_write, file, ensure_ascii=False, indent=4)


def extract_data(nutrition_text, name, description):
    patterns = {
        "Calories": r"(\d+\.?\d*)ккал Калорійність",
        "Fats": r"(\d+\.?\d*)г Жири",
        "Carbs": r"(\d+\.?\d*)г Вуглеводи",
        "Proteins": r"(\d+\.?\d*)г Білки",
        "Unsaturated fats": r"НЖК:\n(\d+\.?\d*)г",
        "Sugar": r"Цукор:\n(\d+\.?\d*)г",
        "Salt": r"Сіль:\n(\d+\.?\d*)г",
        "Portion": r"Порція:\n(\d+\.?\d*)г"
    }

    nutrition_info = {
        "Name": name,
        "Description": description
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, nutrition_text)
        if match:
            unit = "ккал" if key == "Калорійність" else "г"
            nutrition_info[key] = match.group(1) + unit
    return nutrition_info
