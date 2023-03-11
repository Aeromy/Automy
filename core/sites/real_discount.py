import requests


def scrape_real_discount():
    """
    Scrape Real Discount
    :return: list
    """
    url = "https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page=100&orderby=date&free=1&editorschoices=0"
    timeout = 5
    r = requests.get(url=url, timeout=timeout)
    return [item["url"] for item in r.json()["results"]]
