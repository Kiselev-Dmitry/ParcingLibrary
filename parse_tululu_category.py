import os
import argparse
import logging
import time
import json

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("Page was redirected to Main library page.")


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.select_one('h1').text.split("::")
    title = title.strip()
    author = author.strip()

    genres_elements = soup.select("span.d_book a")
    genres = [element.text for element in genres_elements]

    image_tag = soup.select_one(".bookimage a img")
    image = image_tag["src"]
    image_url = urljoin(response.url, image)
    image_dir, image_name = os.path.split(image)

    comments_elements = soup.select(".texts span")
    comments = [comment.text for comment in comments_elements]

    return {
        "title": title,
        "author": author,
        "comments": comments,
        "genres": genres,
        "image_name": image_name,
        "image_url": image_url,
    }


def download_txt(book_url, index, title, books_folder):
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)
    file_name = '{}. {}.txt'.format(index, sanitize_filename(title))
    file_path = os.path.join(books_folder, file_name).replace("\\", os.sep)
    save_file(response, file_path)
    return file_path


def download_image(image_name, image_url, image_folder):
    response = requests.get(image_url)
    response.raise_for_status()
    file_path = os.path.join(image_folder, image_name).replace("\\", os.sep)
    save_file(response, file_path)
    return file_path


def save_file(response, file_path):
    with open(file_path, 'wb') as file:
        file.write(response.content)


def main():
    books_folder = "books"
    image_folder = "images"
    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(image_folder, exist_ok=True)
    books = []
    index = 1
    for page in range(1, 2):  # ЗАМЕНИТЬ !!!
        response = requests.get("https://tululu.org/l55/{}".format(str(page)))
        response.raise_for_status()
        check_for_redirect(response)

        soup = BeautifulSoup(response.text, 'lxml')
        book_tags = soup.select(".d_book")
        for book_tag in book_tags:
            book_href = book_tag.select_one("a")["href"]
            book_url = urljoin("https://tululu.org", book_href)
            print(book_url) # отладочный принт

            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book_info = parse_book_page(response)

            book_path = download_txt(book_url, index, book_info["title"], books_folder)

            image_path = download_image(book_info["image_name"], book_info["image_url"], image_folder)

            books.append({
                "title": book_info["title"],
                "author": book_info["author"],
                "book_path": book_path,
                "image_path": image_path,
                "genres": book_info["genres"],
                "comments": book_info["comments"]
            })
            index += 1

        books_json = json.dumps(books, ensure_ascii=False)
        with open("books.json", "w", encoding="UTF-8") as my_file:
            my_file.write(books_json)


if __name__ == '__main__':
    main()