import requests
import os
import argparse
import logging
import time
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("Page was redirected to Main library page.")


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')

    title, author = soup.find('h1').text.split("::")
    title = title.strip()
    author = author.strip()

    genres_elements = soup.find("span", class_="d_book").find_all("a")
    genres = [element.text for element in genres_elements]

    image = soup.find(class_='bookimage').find('img')['src']
    image_url = urljoin(response.url, image)
    image_dir, image_name = os.path.split(image)

    return title, author, genres, image_name, image_url


def download_txt(url, index, title, books_folder):
    payload = {"id": index}
    response = requests.get("{}txt.php".format(url), params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    file_name = '{}. {}.txt'.format(index, sanitize_filename(title))
    save_file(response, file_name, books_folder)


def download_image(image_name, image_url, image_folder):
    response = requests.get(image_url)
    response.raise_for_status()
    save_file(response, image_name, image_folder)


def save_file(response, file_name, folder):
    file_path = os.path.join(folder, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def main():
    url = "https://tululu.org/"
    books_folder = "books"
    image_folder = "images"
    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(image_folder, exist_ok=True)
    parser = argparse.ArgumentParser(
        description='Скачивание книг и информации о них'
    )
    parser.add_argument(
        '-start_id', help='С какой страницы скачивать',
        type=int, default=1,
    )
    parser.add_argument(
        '-end_id', help='До какой страницы скачивать',
        type=int, default=0
    )
    args = parser.parse_args()
    if not args.end_id:
        args.end_id = args.start_id + 1

    for index in range(args.start_id, args.end_id+1):
        while True:
            try:
                response = requests.get("{}b{}/".format(url, index))
                response.raise_for_status()
                check_for_redirect(response)
                title, author, genres, image_name, image_url = parse_book_page(response)
                download_txt(url, index, title, books_folder)
                download_image(image_name, image_url, image_folder)
                print("Заголовок: ", title)
                print("Автор: ", author)
                print("Жанр: ", genres)
                print("Ссылка на картинку: ", image_url)
            except requests.HTTPError as error:
                logging.warning(error)
                break
            except requests.ConnectionError as error:
                logging.error(error)
                time.sleep(5)
            break

if __name__ == '__main__':
    main()
