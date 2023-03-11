import json
import random
from datetime import datetime
import browser_cookie3
from bs4 import BeautifulSoup
from requests.sessions import Session
from requests.utils import dict_from_cookiejar
from urllib.parse import parse_qs, urlparse, urlsplit
from inquirer.errors import ValidationError as InquirerValidationError


from .exceptions import ElementNotFoundException


def get_cookies_dict():
    """
    Get cookies from the browser.
    :return: dict
    """
    cookie_jar = browser_cookie3.load(domain_name="udemy.com")
    return dict_from_cookiejar(cookie_jar)


def generate_random_ip() -> str:
    """
    Generate random IP address.
    :return: str
    """
    return str(".".join(map(str, (random.randint(0, 255) for _ in range(4)))))


def set_header(access_token: str, forworded_for: str) -> dict:
    """
    Set header for requests.
    :param access_token: str
    :return: dict
    """
    return {
        "authorization": f"Bearer {access_token}",
        "accept": "application/json, text/plain, */*",
        "x-requested-with": "XMLHttpRequest",
        "x-forwarded-for": forworded_for,
        "x-udemy-authorization": f"Bearer {access_token}",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.udemy.com",
        "referer": "https://www.udemy.com/",
        "dnt": "1",
    }


def create_session(headers: dict, cookies: dict) -> Session:
    """
    Create a session.
    :param headers: dict
    :param cookies: dict
    :return: Session
    """
    with Session() as session:
        session.headers.update(headers)
        session.cookies.update(cookies)
    return session


# def get_sitemap(
#     session: Session, headers: dict, cookies: dict, timeout: int
# ) -> BeautifulSoup:
#     """
#     Get sitemap.
#     :param session: Session
#     :param headers: dict
#     :param cookies: dict
#     :return: BeautifulSoup
#     """
#     url = "https://www.udemy.com/sitemap/"
#     r = session.get(url=url, headers=headers, cookies=cookies, timeout=timeout)
#     return BeautifulSoup(r.content, "html.parser")


# def get_categories(soup: BeautifulSoup) -> list:
#     """
#     Get categories.
#     :param soup: BeautifulSoup
#     :return: list
#     """
#     # Get all categories.
#     categories = []
#     for row_el in soup.select("div.row.row-gap-md"):
#         for column_el in row_el.select("div.column.column-3"):
#             column_title_el = column_el.select_one("b")
#             if not column_title_el:
#                 raise ElementNotFoundException("Column title not found.")

#             column_title: str = column_title_el.text.strip()
#             categories.append(column_title)

#     return categories


# def get_languages(soup: BeautifulSoup) -> list:
#     """
#     Get languages.
#     :param soup: BeautifulSoup
#     :return: list
#     """
#     # Get start and end elements.
#     start = soup.select_one("h2:-soup-contains('Local homepages')")
#     if not start:
#         raise ElementNotFoundException("Start element not found.")
#     end = soup.select_one("h2:-soup-contains('Popular topics')")
#     if not end:
#         raise ElementNotFoundException("End element not found.")

#     # Get all rows between start and end.
#     rows = []
#     for sibling in start.next_siblings:
#         if sibling == end:
#             break
#         if not str(sibling).strip():
#             continue
#         rows.append(sibling)

#     # Get all languages.
#     languages = []
#     for row_el in rows:
#         for column_el in row_el.select("div.column.column-3"):
#             column_title_el = column_el.select_one("a")
#             if not column_title_el:
#                 raise ElementNotFoundException("Column title not found.")

#             column_title: str = column_title_el.text.strip()
#             languages.append(column_title)

#     return languages


def get_user_data(session: Session, timeout: int) -> dict:
    """
    Get user data.
    :param session: Session
    :param timeout: int
    :return: dict
    """
    url = "https://www.udemy.com/api-2.0/contexts/me/?me=True&Config=True"

    return session.get(url=url, timeout=timeout).json()


def check_authentication(data: dict) -> bool:
    """
    Check if the user is authenticated.
    :param data: dict
    :return: bool
    """
    try:
        return bool(data["me"]["is_authenticated"])
    except KeyError:
        return False


def get_currency(data: dict) -> str:
    """
    Get currency.
    :param data: dict
    :return: str
    """
    try:
        return data["Config"]["price_country"]["currency"]
    except KeyError:
        return "usd"


def validate_course_url(url: str) -> bool:
    """
    Validate course URL.
    :param url: str
    :return: bool
    """
    result = urlparse(url=url)
    if (result.netloc != "udemy.com") and (result.netloc != "www.udemy.com"):
        return False
    if not result.path.startswith("/course/"):
        return False
    if "couponCode" not in result.query:
        return False
    return True


def get_course_id(session: Session, timeout: int, url: str) -> int:
    """
    Get course ID.
    :param session: Session
    :param timeout: int
    :param url: str
    :return: int
    """
    r = session.get(url=url, timeout=timeout)
    soup = BeautifulSoup(r.content, "html.parser")

    # Get course ID
    el = soup.select_one('meta[itemprop="image"]')
    if not el:
        raise ElementNotFoundException("Course ID not found.")
    return int(el.attrs["content"].split("/")[5].split("_")[0])


def get_course_details(session: Session, timeout: int, course_id: int) -> dict:
    """
    Get course details.
    :param session: Session
    :param timeout: int
    :param course_id: int
    :return: dict
    """
    url = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=locale,primary_category,avg_rating_recent,visible_instructors,created,avg_rating,archive_time,is_paid,is_private,num_subscribers,price,title,url,image_480x270,status_label,primary_subcategory"
    return session.get(url=url, timeout=timeout).json()


def check_course_details(data: dict) -> dict:
    """
    Check if the course details are valid.
    :param data: dict
    :return: dict
    """
    id = data["id"]
    title = data["title"]
    url = "https://www.udemy.com" + data["url"]
    category = data["primary_category"]["title"]
    sub_category = data["primary_subcategory"]["title"]
    language = data["locale"]["simple_english_title"]
    rating = data["avg_rating"]
    instructors = [
        instructor["display_name"] for instructor in data["visible_instructors"]
    ]
    image = data["image_480x270"]
    is_paid = data["is_paid"]
    is_private = data["is_private"]
    status_label = data["status_label"]
    price = data["price"]
    num_subscribers = data["num_subscribers"]
    created = datetime.strptime(data["created"], "%Y-%m-%dT%H:%M:%SZ").strftime(
        "%B %d, %Y"
    )

    return {
        "id": id,
        "title": title,
        "url": url,
        "category": category,
        "sub_category": sub_category,
        "language": language,
        "rating": rating,
        "instructors": instructors,
        "image": image,
        "is_paid": is_paid,
        "is_private": is_private,
        "status_label": status_label,
        "price": price,
        "num_subscribers": num_subscribers,
        "created": created,
    }


def validate_min_ratings(answers, current) -> bool:
    """
    Check minimum rating.
    :param rating: str
    :return: bool
    """
    try:
        ratings = float(current)
    except ValueError:
        raise InquirerValidationError(
            value=current,
            reason="Please enter a valid number",
        )
    if ratings < 0.0 or ratings > 5.0:
        raise InquirerValidationError(
            value=ratings,
            reason="Please enter a number between 0.0 and 5.0",
        )
    return True


def validate_min_subscribers(answers, current) -> bool:
    """
    Check minimum subscribers.
    :param subscribers: str
    :return: bool
    """
    try:
        subscribers = int(current)
    except ValueError:
        raise InquirerValidationError(
            value=current,
            reason="Please enter a valid number",
        )
    if subscribers < 0:
        raise InquirerValidationError(
            value=subscribers,
            reason="Please enter a number greater than 0",
        )
    return True


def extract_coupon_code(url: str) -> str:
    """
    Extract coupon code from URL.
    :param url: str
    :return: str
    """
    query = urlsplit(url).query
    params = parse_qs(query)
    try:
        params = {k: v[0] for k, v in params.items()}
        return params["couponCode"]
    except KeyError:
        raise KeyError("Coupon code not found.")


def get_purchase_details(
    session: Session,
    timeout: int,
    course_id: int,
    coupon_code: str,
) -> dict:
    """
    Get purchase details.
    :param session: Session
    :param timeout: int
    :param course_id: int
    :param coupon_code: int
    :return: dict
    """
    url = f"https://www.udemy.com/api-2.0/course-landing-components/{course_id}/me/?components=purchase,redeem_coupon&couponCode={coupon_code}"

    return session.get(url=url, timeout=timeout).json()


def check_purchase_details(data: dict) -> dict:
    """
    Check if the course is purchased.
    :param data: dict
    :return: dict
    """
    purchased = data["redeem_coupon"]["has_already_purchased"]
    valid_coupon = data["purchase"]["data"]["pricing_result"]["discount_percent"] == 100
    uses_remaining = data["purchase"]["data"]["pricing_result"]["campaign"][
        "uses_remaining"
    ]
    uses_remaining = uses_remaining if uses_remaining else 0
    code = data["purchase"]["data"]["pricing_result"]["campaign"]["code"]

    return {
        "code": code,
        "purchased": purchased,
        "valid_coupon": valid_coupon,
        "uses_remaining": uses_remaining,
    }


def enroll_course(
    session: Session,
    timeout: int,
    course_id: int,
    coupon_code: str,
    currency: str,
) -> dict:
    """
    Enroll in a course.
    :param session: Session
    :timeout: int
    :param course_id: int
    :param coupon: str
    :param currency: str
    :return: dict
    """
    url = "https://www.udemy.com/payment/checkout-submit/"
    payload = json.dumps(
        {
            "checkout_environment": "Marketplace",
            "checkout_event": "Submit",
            "shopping_info": {
                "items": [
                    {
                        "discountInfo": {"code": coupon_code},
                        "buyable": {"type": "course", "id": course_id},
                        "price": {"amount": 0, "currency": currency},
                    }
                ]
            },
            "payment_info": {"payment_vendor": "Free", "payment_method": "free-method"},
        }
    )
    return session.post(url=url, timeout=timeout, data=payload).json()
