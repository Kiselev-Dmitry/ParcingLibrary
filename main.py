import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse


def download_txt(url, id, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    payload = {"id": id}
    response = requests.get("{}txt.php".format(url), params=payload)
    response.raise_for_status()
    if not response.history:
        file_name = '{}. {}.txt'.format(id, sanitize_filename(get_title(url, id)))
        save_file(response, file_name, folder)
        download_image(url, id)


def get_title(url, id):
    response = requests.get("{}b{}/".format(url, id))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.split("::")
    title = title.strip()
    print("Заголовок: ", title)
    return title


def download_image(url, id):
    response = requests.get("{}b{}/".format(url, id))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    image = soup.find(class_='bookimage').find('img')['src']
    image_url = urljoin(url, image)
    print("Ссылка на картинку: ", image_url)
    dir_name, file_name = os.path.split(image)
    response = requests.get(image_url)
    response.raise_for_status()
    save_file(response, file_name, "images")


def save_file(response, file_name, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    url = "https://tululu.org/"
    folder = 'books/'
    for index in range(1, 11):
        download_txt(url, str(index), folder)
