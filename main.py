import requests
import os

books_dir = "books"
if not os.path.exists(books_dir):
    os.makedirs(books_dir)

# url = "https://tululu.org/txt.php?id=32168"
url = "https://tululu.org/txt.php"

for i in range(9):
    payload = {"id": str(i)}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    filename = '{}/book{}.txt'.format(books_dir, i)
    with open(filename, 'wb') as file:
        file.write(response.content)
