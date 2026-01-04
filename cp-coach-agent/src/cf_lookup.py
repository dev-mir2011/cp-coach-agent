import cloudscraper
import json
import os
import sys
import time
from bs4 import BeautifulSoup


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works in dev and PyInstaller exe"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


data_path = resource_path("../data")
CACHE_FILE = os.path.join(data_path, "cf_cache.json")
SLEEP_SECONDS = 2
MAX_RETRIES = 3
RETRY_BACKOFF = 5

REQUIRED_FIELDS = {
    "contest_id",
    "index",
    "rating",
    "title",
    "time_limit",
    "memory_limit",
    "statement",
    "input",
    "output",
    "url",
}

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "desktop": True}
)


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CACHE_FILE)


def get_problem_rating(problem_key: str) -> int | None:
    api_url = "https://codeforces.com/api/problemset.problems"
    r = scraper.get(api_url, timeout=30)
    data = r.json()

    for p in data["result"]["problems"]:
        key = f"{p.get('contestId')}{p.get('index')}"
        if key == problem_key and "rating" in p:
            return p["rating"]

    return None


def is_valid_entry(entry: dict) -> bool:
    for field in REQUIRED_FIELDS:
        if field not in entry:
            return False
        if entry[field] is None:
            return False
        if isinstance(entry[field], str) and entry[field].strip() == "":
            return False
    return True


def lookup_or_scrape(problem_key: str) -> dict | None:
    cache = load_cache()

    if problem_key in cache and is_valid_entry(cache[problem_key]):
        return cache[problem_key]

    contest_id = "".join(filter(str.isdigit, problem_key))
    index = "".join(filter(str.isalpha, problem_key)).upper()
    url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"

    rating = get_problem_rating(problem_key)
    if rating is None:
        return None  # rating is mandatory

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = scraper.get(url, timeout=20)
            if r.status_code != 200:
                raise Exception("Blocked")

            soup = BeautifulSoup(r.text, "html.parser")

            statement_div = soup.find("div", class_="problem-statement")
            title_div = soup.find("div", class_="title")
            time_limit = soup.find("div", class_="time-limit")
            memory_limit = soup.find("div", class_="memory-limit")

            if not statement_div or not title_div:
                raise Exception("HTML structure changed")

            input_spec = statement_div.find("div", class_="input-specification")
            output_spec = statement_div.find("div", class_="output-specification")

            problem_data = {
                "contest_id": int(contest_id),
                "index": index,
                "rating": rating,
                "title": title_div.get_text(strip=True),
                "time_limit": time_limit.get_text(strip=True) if time_limit else "",
                "memory_limit": (
                    memory_limit.get_text(strip=True) if memory_limit else ""
                ),
                "statement": statement_div.get_text("\n", strip=True),
                "input": input_spec.get_text("\n", strip=True) if input_spec else "",
                "output": output_spec.get_text("\n", strip=True) if output_spec else "",
                "url": url,
            }

            if not is_valid_entry(problem_data):
                return None

            cache[problem_key] = problem_data
            save_cache(cache)

            time.sleep(SLEEP_SECONDS)
            return problem_data

        except Exception:
            if attempt == MAX_RETRIES:
                return None
            time.sleep(RETRY_BACKOFF)
