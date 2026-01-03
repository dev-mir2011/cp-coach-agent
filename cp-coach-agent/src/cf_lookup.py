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
# CACHE_FILE = "cf_cache.json"
SLEEP_SECONDS = 2
MAX_RETRIES = 3
RETRY_BACKOFF = 5

REQUIRED_FIELDS = {
    "title",
    "statement",
    "input",
    "output",
    "time_limit",
    "memory_limit",
}

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "desktop": True}
)


def lookup_or_scrape(problem_key: str) -> dict:
    """
    Checks cache for a Codeforces problem.
    - Returns the cached problem if present and valid.
    - Otherwise scrapes the problem, updates cache, and returns the dict.
    Returns None if scraping fails after retries.
    """
    # Load cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

    # Return cached problem if valid
    if problem_key in cache:
        entry = cache[problem_key]
        if all(
            field in entry and entry[field].strip() != "" for field in REQUIRED_FIELDS
        ):
            return entry

    # Parse contest_id and index
    contest_id = "".join(filter(str.isdigit, problem_key))
    index = "".join(filter(str.isalpha, problem_key)).upper()
    url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = scraper.get(url, timeout=20)
            if r.status_code != 200:
                raise Exception(f"Blocked ({r.status_code})")

            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("div", class_="title")
            time_limit = soup.find("div", class_="time-limit")
            memory_limit = soup.find("div", class_="memory-limit")
            statement = soup.find("div", class_="problem-statement")

            if not title or not statement:
                raise Exception("Problem HTML structure not found")

            description = statement.find("div", recursive=False).get_text(
                "\n", strip=True
            )
            input_spec = statement.find("div", class_="input-specification")
            output_spec = statement.find("div", class_="output-specification")

            problem_data = {
                "contest_id": int(contest_id),
                "index": index,
                "title": title.get_text(strip=True),
                "time_limit": (
                    time_limit.get_text(strip=True).replace("Time limit:", "").strip()
                    if time_limit
                    else ""
                ),
                "memory_limit": (
                    memory_limit.get_text(strip=True)
                    .replace("Memory limit:", "")
                    .strip()
                    if memory_limit
                    else ""
                ),
                "statement": description,
                "input": input_spec.get_text("\n", strip=True) if input_spec else "",
                "output": output_spec.get_text("\n", strip=True) if output_spec else "",
                "url": url,
            }

            # Save to cache
            cache[problem_key] = problem_data
            tmp = CACHE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            os.replace(tmp, CACHE_FILE)

            time.sleep(SLEEP_SECONDS)
            return problem_data

        except Exception:
            if attempt == MAX_RETRIES:
                return None
            else:
                time.sleep(RETRY_BACKOFF)


if __name__ == "__main__":
    problem = lookup_or_scrape("116A")
    print(problem)
