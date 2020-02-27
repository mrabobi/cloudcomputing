from concurrent.futures.thread import ThreadPoolExecutor

import requests


def get_data():
    url = "http://127.0.0.1:5000/random?n=50"
    print(requests.get(url))


with ThreadPoolExecutor(max_workers=999) as executor:
    Future_list = [executor.submit(get_data) for i in range(999)]


