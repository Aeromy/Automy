import requests


def scrape_enext():
    """
    Scrape E-Next
    :return: list
    """
    url = "https://jobs.e-next.in/public/assets/data/udemy.json"
    timeout = 5
    r = requests.get(url=url, timeout=timeout)
    return [item["site"] for item in r.json()]
