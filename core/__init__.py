from .base import (
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
    get_currency,
    validate_min_ratings,
    validate_min_subscribers,
    get_purchase_details,
    extract_coupon_code,
    check_purchase_details,
    enroll_course,
)
from .exceptions import ElementNotFoundException
from .sites.e_next import scrape_enext
from .sites.real_discount import scrape_real_discount
