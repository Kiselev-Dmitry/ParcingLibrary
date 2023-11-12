import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse


def parse_book_page(url, id):
    response = requests.get("{}b{}/".format(url, id))
    response.raise_for_status()
    if not response.history:
        soup = BeautifulSoup(response.text, 'lxml')

        title, author = soup.find('h1').text.split("::")
        title = title.strip()
        author = author.strip()
        print("Заголовок: ", title)
        print("Автор: ", author)

        genres_elements = soup.find("span", class_="d_book").find_all("a")
        genres = []
        for element in genres_elements:
            genres.append(element.text)
        print("Жанр: ", genres)

        image = soup.find(class_='bookimage').find('img')['src']
        image_url = urljoin(url, image)
        image_dir, image_name = os.path.split(image)
        print("Ссылка на картинку: ", image_url) # отладочный код

        return title, image_name, image_url


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
        title, image_name, image_url = parse_book_page(url, str(id))
        file_name = '{}. {}.txt'.format(id, sanitize_filename(title))
        save_file(response, file_name, folder)
        download_image(image_name, image_url, id)


def download_image(image_name, image_url, id):
    image_folder = "images"
    response = requests.get(image_url)
    response.raise_for_status()
    save_file(response, image_name, image_folder)


def save_file(response, file_name, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)


# def main():
#     url = "https://tululu.org/"
#     folder = 'books/'
#     for index in range(1, 11):
#        download_txt(url, str(index), folder)


if __name__ == '__main__':
    url = "https://tululu.org/"
    folder = 'books/'
    for index in range(1, 11):
       download_txt(url, str(index), folder)
