import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def get_title(url, id):
#    url = "{}b{}/".format(url, id)
    response = requests.get("{}b{}/".format(url, id))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('h1').text.split("::")
    title = title.strip()
#    author = author.strip()
#    print("Заголовок: ", title)
#    print("Автор: ", author)
    return title


def download_txt(url, id, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
#    url = "{}txt.php".format(main_url)
    payload = {"id": id}
    response = requests.get("{}txt.php".format(url), params=payload)
    response.raise_for_status()
    if not response.history:
        filename = '{}. {}.txt'.format(id, sanitize_filename(get_title(url, id)))
        file_path = os.path.join(folder, filename)
#        print(file_path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(file_path, 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    url = "https://tululu.org/"
    folder = 'books/'
    for index in range(1, 11):
        download_txt(url, str(index), folder)
