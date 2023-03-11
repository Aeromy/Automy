import time
import random
import inquirer
from inquirer.themes import GreenPassion
from requests.exceptions import Timeout

# local
from cli import CustomPrint, Arguments
from core import (
    get_cookies_dict,
    generate_random_ip,
    set_header,
    create_session,
    get_user_data,
    check_authentication,
    validate_course_url,
    get_course_id,
    get_course_details,
    check_course_details,
    extract_coupon_code,
    get_purchase_details,
    check_purchase_details,
    validate_min_ratings,
    validate_min_subscribers,
    get_currency,
    enroll_course,
)
from core import ElementNotFoundException
from core.sites.e_next import scrape_enext
from core.sites.real_discount import scrape_real_discount


DEBUG = Arguments.debug()
CONSOLE_THEME = GreenPassion()
DEFAULT_TIMEOUT = 5
CATEGORIES = [
    "Development",
    "Business",
    "Finance & Accounting",
    "IT & Software",
    "Office Productivity",
    "Personal Development",
    "Design",
    "Marketing",
    "Lifestyle",
    "Photography & Video",
    "Health & Fitness",
    "Music",
    "Teaching & Academics",
]
LANGUAGES = [
    "English",
    "Spanish",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Russian",
    "Turkish",
    "Arabic",
    "Chinese",
    "Japanese",
    "Korean",
    "Hindi",
    "Indonesian",
    "Malay",
    "Thai",
    "Vietnamese",
    "Bengali",
    "Dutch",
    "Greek",
    "Hebrew",
    "Hungarian",
    "Polish",
    "Romanian",
    "Swedish",
    "Urdu",
    "Czech",
    "Danish",
    "Finnish",
    "Norwegian",
    "Slovak",
    "Ukrainian",
]
INTERVALS = ["0", "5", "10", "15", "20", "25", "30"]


def main():
    # Get cookies.
    cookies = get_cookies_dict()
    # Generate random IP address.
    random_ip = generate_random_ip()
    # Set header.
    headers = set_header(cookies.get("access_token"), random_ip)
    # Create session.
    session = create_session(headers=headers, cookies=cookies)

    # Get user data.
    try:
        user_data = get_user_data(session, timeout=DEFAULT_TIMEOUT)
    except Timeout:
        CustomPrint.error(
            "Request timed out while getting user data. Please try again later."
        )
        return
    except Exception:
        CustomPrint.error("An error occurred while getting user data.")
        return

    # Check if user is authenticated.
    is_authenticated = check_authentication(user_data)
    if not is_authenticated:
        CustomPrint.error(
            f"Authentication failed. Please log into `https://www.udemy.com` with your browser."
        )
        return

    # Get currency.
    currency = get_currency(user_data)

    # Prompt user to select categories.
    categories_name = "categories"
    category_answers = inquirer.prompt(
        [
            inquirer.Checkbox(
                name=categories_name,
                message="Select categories",
                choices=CATEGORIES,
                default=[],
            )
        ],
        theme=CONSOLE_THEME,
    )
    if not category_answers:
        CustomPrint.error("No categories selected.")
        return
    if not category_answers[categories_name]:
        CustomPrint.error("No categories selected.")
        return
    if DEBUG:
        CustomPrint.debug(
            f"Selected categories: {str(category_answers[categories_name])}"
        )

    # Prompt user to select languages.
    languages_name = "languages"
    language_answers = inquirer.prompt(
        [
            inquirer.Checkbox(
                name=languages_name,
                message="Select languages",
                choices=LANGUAGES,
                default=[],
            )
        ],
        theme=CONSOLE_THEME,
    )
    if not language_answers:
        CustomPrint.error("No languages selected.")
        return
    if not language_answers[languages_name]:
        CustomPrint.error("No languages selected.")
        return
    if DEBUG:
        CustomPrint.debug(
            f"Selected languages: {str(language_answers[languages_name])}"
        )

    # Prompt user for minimum course ratings
    min_ratings_name = "ratings"
    min_ratings = inquirer.prompt(
        [
            inquirer.Text(
                name=min_ratings_name,
                message="Enter minimum course ratings (0.0 to 5.0)",
                default="0.0",
                validate=validate_min_ratings,
            )
        ],
        theme=CONSOLE_THEME,
    )
    if not min_ratings:
        CustomPrint.error("No minimum course rating provided.")
        return
    if not min_ratings[min_ratings_name]:
        CustomPrint.error("No minimum course ratings provided.")
        return
    if DEBUG:
        CustomPrint.debug(
            f"Selected minimum ratings {float(min_ratings[min_ratings_name])}"
        )

    # Prompt user for minimum subscribers
    min_subscribers_name = "subscribers"
    min_subscribers = inquirer.prompt(
        [
            inquirer.Text(
                name=min_subscribers_name,
                message="Enter minimum course subscribers",
                default="0",
                validate=validate_min_subscribers,
            )
        ],
        theme=CONSOLE_THEME,
    )
    if not min_subscribers:
        CustomPrint.error("No minimum course subscribers provided.")
        return
    if not min_subscribers[min_subscribers_name]:
        CustomPrint.error("No minimum course subscribers provided.")
        return
    if DEBUG:
        CustomPrint.debug(
            f"Selected minimum subscribers {int(min_subscribers[min_subscribers_name])}"
        )

    # Prompt user for interval
    interval_name = "interval"
    interval = inquirer.prompt(
        [
            inquirer.List(
                name=interval_name,
                message="Select interval",
                choices=INTERVALS,
                default=INTERVALS[0],
            )
        ],
        theme=CONSOLE_THEME,
    )
    if not interval:
        CustomPrint.error("No interval selected.")
        return
    if not interval[interval_name]:
        CustomPrint.error("No interval selected.")
        return
    if DEBUG:
        CustomPrint.debug(f"Selected interval {int(interval[interval_name])}")

    # Scrape links.
    links = []

    # E-Next
    try:
        enext_links = scrape_enext()
        links.extend(enext_links)
    except Timeout:
        CustomPrint.error(
            "Request timed out while scraping [bold dark_orange]E-Next[/bold dark_orange]."
        )
        return
    except Exception:
        CustomPrint.error(
            "An error occurred while scraping [bold dark_orange]E-Next[/bold dark_orange]."
        )
        return

    # Real Discount
    try:
        real_discount_links = scrape_real_discount()
        links.extend(real_discount_links)
    except Timeout:
        CustomPrint.error(
            "Request timed out while scraping [bold dark_orange]Real Discount[/bold dark_orange]."
        )
        return
    except Exception:
        CustomPrint.error(
            "An error occurred while scraping [bold dark_orange]Real Discount[/bold dark_orange]."
        )
        return

    links = list(set(links))  # remove duplicates
    random.shuffle(links)  # shuffle links

    # save enrolled courses
    enrolls = []

    # Enroll in courses.
    for index, link in enumerate(links):
        if index != 0:  # Don't wait for the first link
            CustomPrint.info(f"Wait {int(interval[interval_name])} seconds...")
            print("\n")
            time.sleep(int(interval[interval_name]))

        CustomPrint.info(f"Link {index+1} of {len(links)}")
        CustomPrint.info(link)

        if not validate_course_url(link):
            CustomPrint.info(
                f"Skipping course [bold dark_orange]Invalid URL[/bold dark_orange]"
            )
            continue

        # Get course ID
        try:
            course_id = get_course_id(
                session=session,
                timeout=DEFAULT_TIMEOUT,
                url=link,
            )
        except Timeout:
            CustomPrint.error("Request timed out while getting course ID.")
            continue
        except ElementNotFoundException as e:
            CustomPrint.error(e.args[0])
            continue
        except Exception:
            CustomPrint.error("An error occurred while getting course ID.")
            continue

        # Get course details
        try:
            course_details = get_course_details(
                session=session,
                timeout=DEFAULT_TIMEOUT,
                course_id=course_id,
            )
        except Timeout:
            CustomPrint.error("Request timed out while getting course details.")
            continue
        except Exception:
            CustomPrint.error("An error occurred while getting course details.")
            continue

        # Check course details
        try:
            valid_course = check_course_details(course_details)
        except Exception:
            CustomPrint.error("An error occurred while checking course details.")
            continue
        if DEBUG:
            CustomPrint.debug(f"Course details: {str(valid_course)}")

        # Check if course is valid
        if not valid_course["is_paid"]:
            CustomPrint.info(
                f"Skipping course [bold dark_orange]Free[/bold dark_orange]."
            )
            continue
        if valid_course["is_private"]:
            CustomPrint.info(
                f"Skipping course [bold dark_orange]Private[/bold dark_orange]."
            )
            continue
        if valid_course["status_label"] != "Live":
            CustomPrint.info(
                f"Skipping course [bold dark_orange]Inactive[/bold dark_orange]."
            )
            continue
        course_category = valid_course["category"]
        if not course_category in category_answers[categories_name]:
            CustomPrint.info(
                f"Skipping course category [bold dark_orange]{course_category}[/bold dark_orange]."
            )
            continue
        course_language = valid_course["language"]
        if not course_language in language_answers[languages_name]:
            CustomPrint.info(
                f"Skipping course language [bold dark_orange]{valid_course['language']}[/bold dark_orange]."
            )
            continue
        course_rating = round(float(valid_course["rating"]), 1)
        if course_rating < float(min_ratings[min_ratings_name]):
            CustomPrint.info(
                f"Skipping course rating [bold dark_orange]{course_rating}[/bold dark_orange]."
            )
            continue
        course_num_subscribers = int(valid_course["num_subscribers"])
        if course_num_subscribers < int(min_subscribers[min_subscribers_name]):
            CustomPrint.info(
                f"Skipping course subscribers [bold dark_orange]{course_num_subscribers}[/bold dark_orange]."
            )
            continue

        # Get coupon code
        try:
            coupon_code = extract_coupon_code(url=link)
        except KeyError as e:
            CustomPrint.error(e.args[0])
            continue
        except Exception:
            CustomPrint.error("An error occurred while extracting coupon code.")
            continue

        # Get purchase details
        try:
            purchase_details = get_purchase_details(
                session=session,
                timeout=DEFAULT_TIMEOUT,
                course_id=course_id,
                coupon_code=coupon_code,
            )
        except Timeout:
            CustomPrint.error("Request timed out while getting purchase details.")
            continue
        except Exception:
            CustomPrint.error("An error occurred while getting purchase details.")
            continue

        # Check purchase details
        try:
            valid_purchase = check_purchase_details(purchase_details)
        except Exception:
            CustomPrint.error("An error occurred while checking purchase details.")
            continue
        if DEBUG:
            CustomPrint.debug(f"Purchase details: {str(valid_purchase)}")

        if valid_purchase["purchased"]:
            CustomPrint.info(
                "Skipping course [bold dark_orange]Already Purchased[/bold dark_orange]."
            )
            continue
        if not valid_purchase["valid_coupon"]:
            CustomPrint.info(
                "Skipping course [bold dark_orange]Invalid Coupon[/bold dark_orange]."
            )
            continue

        try:
            enroll_data = enroll_course(
                session=session,
                timeout=DEFAULT_TIMEOUT,
                course_id=course_id,
                coupon_code=coupon_code,
                currency=currency,
            )
        except Timeout:
            CustomPrint.error("Request timed out while enrolling course.")
            continue
        except Exception:
            CustomPrint.error("An error occurred while enrolling course.")
            continue

        if enroll_data["status"] != "succeeded":
            CustomPrint.error("Course enrollment failed.")
            continue

        enrolls.append(link)
        CustomPrint.success(f"Course enrolled successfully.")

    print("\n")
    CustomPrint.success(f"YOU'VE SUCCESSFULLY ENROLLED IN {len(enrolls)} COURSES.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        CustomPrint.success("Successfully exited.")
    except Exception:
        CustomPrint.error("An error occurred.")
