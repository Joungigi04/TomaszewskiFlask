from flask import Flask, request, Response, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import re

app = Flask(__name__)

def get_difficulty_value(driver):
    try:
        element = driver.find_element(By.CSS_SELECTOR, "[class*='parm-difficulty-']")
        class_attr = element.get_attribute("class")  # np. "parm-difficulty-1 flex"
        match = re.search(r"parm-difficulty-(\d+)", class_attr)
        if match:
            return match.group(1)
    except:
        pass
    return None

def get_animal_value(driver):
    try:
        element = driver.find_element(By.CSS_SELECTOR, "[class*='animal-']")
        class_attr = element.get_attribute("class")  # np. "animal-1 flex"
        match = re.search(r"animal-(\d+)", class_attr)
        if match:
            val = match.group(1)
            if val == "0":
                return "Bezpieczna dla zwierząt"
            elif val == "1":
                return "Szkodliwa dla zwierząt"
        return "Nieznany status"
    except:
        return None

def get_scale_value(driver, css_selector):
    try:
        element = driver.find_element(By.CSS_SELECTOR, css_selector)
        class_attr = element.get_attribute("class")  # np. "parm-cleaning scale-3"
        match = re.search(r"scale-(\d+)", class_attr)
        if match:
            return match.group(1)
    except:
        pass
    return None

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Brak URL"}), 400

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Wyszukiwanie ceny
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, "span[itemprop='price']")
        price = price_element.text.strip()
    except:
        # Jeśli nie znaleziono itemprop='price'
        try:
            price_element_alt = driver.find_element(By.CSS_SELECTOR, ".current-price span")
            # Pobieramy wartość atrybutu 'content', bo tekst może być pusty
            price = price_element_alt.get_attribute("content")
            if not price:
                price = "Nie znaleziono ceny"
        except:
            price = "Nie znaleziono ceny"

    # Pierwsze zdjęcie produktu
    try:
        img_element = driver.find_element(By.CSS_SELECTOR, ".product-cover img")
        image_url = img_element.get_attribute("src")
    except:
        image_url = "Nie znaleziono zdjęcia"

    # Poziom trudności (parm-difficulty-X)
    difficulty = get_difficulty_value(driver)

    # Bezpieczeństwo dla zwierząt (animal-0 / animal-1)
    animal_status = get_animal_value(driver)

    # Oczyszczanie powietrza (parm-cleaning scale-X)
    air_cleaning = get_scale_value(driver, ".parm-cleaning")

    # Nasłonecznienie (parm-sun scale-X)
    sunlight = get_scale_value(driver, ".parm-sun")

    # Podlewanie (parm-water scale-X)
    watering = get_scale_value(driver, ".parm-water")

    driver.quit()

    response_data = {
        "url": url,
        "price": price,
        "image_url": image_url,
        "difficulty": difficulty,
        "animal_status": animal_status,
        "air_cleaning": air_cleaning,
        "sunlight": sunlight,
        "watering": watering
    }

    return Response(
        json.dumps(response_data, ensure_ascii=False, indent=2),
        mimetype="application/json"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
