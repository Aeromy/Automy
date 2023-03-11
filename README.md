![GitHub](https://img.shields.io/github/license/Aeromy/Automy?style=for-the-badge)
![GitHub Repo stars](https://img.shields.io/github/stars/Aeromy/Automy?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/Aeromy/Automy?style=for-the-badge)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Aeromy/Automy?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Aeromy/Automy?style=for-the-badge)
![GitHub last commit](https://img.shields.io/github/last-commit/Aeromy/Automy?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/Aeromy/Automy?style=for-the-badge)
![GitHub top language](https://img.shields.io/github/languages/top/Aeromy/Automy?style=for-the-badge)
![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/Aeromy/Automy?style=for-the-badge)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Aeromy/Automy?style=for-the-badge)
![GitHub repo file count](https://img.shields.io/github/directory-file-count/Aeromy/Automy?style=for-the-badge)
![Lines of code](https://img.shields.io/tokei/lines/github/Aeromy/Automy?style=for-the-badge)

# Automy

This repository contains a Python script that scrapes coupon data from external websites and automatically enrolls you in Udemy courses using those coupons. The script uses web scraping techniques to find and extract coupon codes from coupon websites, and then logs into your Udemy account to enroll you in relevant courses.

## Requirements

-   python 3.x
-   pip

## Installation

1. Clone this repository.
2. Install Python 3.x if not already installed.
3. Install the required dependencies by running `pip install -r requirements.txt` in the cloned repository's root directory.

## Usage

1. Login into your Udemy account at https://www.udemy.com/ using your preferred browser.
2. Run the script by running `python main.py` in the cloned repository's root directory.
3. Follow the prompts to input the category, language, minimum ratings, minimum subscribers, and interval.
4. The script will automatically scrape coupon data from external websites and enroll you in relevant courses on Udemy.

## Debug Mode

You can enable debug mode by using the `-d` or `--debug` flag when running the script. Debug mode will print additional information to the console, such as the scraped coupon codes and enrolled courses.

## Disclaimer

This script is for educational and testing purposes only. The author does not condone or promote the use of this script for illegal or unethical purposes. The author is not responsible for any consequences of using this script in violation of Udemy's terms of service. Use at your own risk.
