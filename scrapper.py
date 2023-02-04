from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import requests
from PIL import Image
import os
import time
import json
import cv2
import numpy as np
import urllib
URL = "https://www.ralphlauren.nl/en/men/clothing/hoodies-sweatshirts/10204?webcat=men%7Cclothing%7Cmen-clothing-hoodies-sweatshirts"


def scrape_images(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"+"AppleWebKit/537.36 (KHTML, like Gecko)"+"Chrome/87.0.4280.141 Safari/537.36")
    driver =  webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    driver.get(url)
    view_all_btn = driver.find_element(by=By.XPATH, value="//a[@class='view-all']")
    driver.execute_script("arguments[0].click();", view_all_btn)
    time.sleep(10)      
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    while_flag = 0
    img_links = []
    img_links_with_person = []
    _dict={}
    while while_flag<10:
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        while_flag+=1
    products = driver.find_elements(by=By.XPATH, value="//div[@class='product-tile ']")
    pictures_size=0
    hover_pictures_size=0

    for product in products:
        category_name = product.find_element(by=By.XPATH, value=".//div[@class='brand-name clearfix']").text
        if 'Polo Ralph Lauren' not in category_name:
            continue
        pic = product.find_element(by=By.XPATH, value=".//picture[@class='rlc-picture']//source[@class='rlc-image-src-desktop']").get_attribute("srcset")
        img_links_with_person.append(pic)
        pic2 = product.find_element(by=By.XPATH, value=".//picture[@class='rlc-picture']//img").get_attribute("onerror")
        pic2 = pic2.split(";")[1]
        pic2 = pic2.split("'")[1]
        img_links.append(pic2)
        try:
            ul_element = product.find_element(by=By.XPATH, value=".//ul[@class='swatch-list']")
            hovers = ul_element.find_elements(by=By.XPATH, value=".//li")
            merger = []
            for hover in hovers:
                hover_img = hover.find_element(by=By.XPATH, value=".//img[@class='swatch-image']").get_attribute("data-thumb")
                res = json.loads(hover_img)
                hover_pictures_size+=1
                if(len(hovers)>1):
                    merger.append(res['src'])
            if(len(merger)>=1):
                merger.append(pic)
                _dict[pictures_size] = merger
        except:
            pass
        
        pictures_size+=1
    
    driver.quit()

    save_images(img_links, img_links_with_person, _dict)


def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)
def save_images_to_folder(links, folder):
    i=0
    for link in links:
        img = Image.open(requests.get(link, stream = True).raw)
        img.save(folder+f"/{i}"+'.jpg')
        i+=1
def save_images(img_links, img_links_with_person, _dict):
    create_folder("images_with_person")
    create_folder("images")
    create_folder("merged")
    save_images_to_folder(img_links_with_person,"images_with_person")
    save_images_to_folder(img_links,"images")
    i=0
    for d in _dict:
        stack_images = []
        images = []
        for url in _dict[d]:
            with urllib.request.urlopen(url) as url:
                s = url.read()
            images.append(cv2.imdecode(np.frombuffer(s, np.uint8), -1))

        width = len(images) * images[0].shape[1]
        height = images[0].shape[0]

        result = np.zeros((height, width, 3), dtype=np.uint8)

        x_offset = 0
        for image in images:
            result[0:image.shape[0], x_offset:x_offset + image.shape[1]] = image
            x_offset += image.shape[1]

        # Save the result
        cv2.imwrite(f"merged/{i}.jpg", result)
        i+=1
scrape_images(URL)

