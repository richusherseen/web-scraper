import io
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image
from selenium import webdriver
import os
from selenium.webdriver.common.by import By
from slugify import slugify
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_content_from_url(url: str) -> str:
    """scrape the content div of diseases

    Args:
        url (str): content url of the website

    Returns:
        str: the inner HTML of the content div
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    content = driver.find_element(
        By.XPATH, "//div[contains(@class,'[ js-content-images ]')]").get_attribute('innerHTML')
    driver.quit()
    return content


def create_data_dictionary(content: str, url: str) -> dict:
    """scrape the disease name, url and the icon from the
    provided content.

    Args:
        content (str): inner HTML of content
        url (str): base URL of the website

    Returns:
        dict: dictionary of the created data set
    """
    soup = BeautifulSoup(content)
    results = {'Name of Disease': [], 'URL': [], 'Icon': []}
    for a in soup.findAll(attrs={"class": 'imageList__group__item'}):
        name = a.find('h6').text
        results['Name of Disease'].append(name)
        results['URL'].append(url + str(a.get('href')))
        icon = save_icon_image(a.find('img').get('src'), name)
        results['Icon'].append(icon)
    return results


def save_result_to_csv(result: dict) -> None:
    """save the given data set into a csv file

    Args:
        result (dict): data set
    """
    df = pd.DataFrame(result)
    df.to_csv("diseases.csv", index=False)


def save_icon_image(image_url: str, name: str) -> str:
    """save the icon image to a folder

    Args:
        image_url (str): url of the icon image
        name (str): name of the disease

    Returns:
        str: file path of the icon image
    """
    image_name = slugify(name) + '.png'
    output_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'img')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    response = requests.get(image_url)
    image_content = response.content
    image_file = io.BytesIO(image_content)
    image = Image.open(image_file).convert("RGB")
    file_path = os.path.join(output_dir, image_name)
    image.save(file_path, "PNG", quality=80)
    return file_path


def main():
    base_url = 'https://dermnetnz.org'
    content_url = f"{base_url}/image-library"
    content = get_content_from_url(content_url)
    result = create_data_dictionary(
        content=content, url=base_url
    )
    save_result_to_csv(result)


if __name__ == "__main__":
    main()
