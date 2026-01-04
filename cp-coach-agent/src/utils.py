import os
import sys
import json
from google import genai
from dotenv import load_dotenv
from cf_lookup import lookup_or_scrape

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works in dev and PyInstaller exe"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


code_prompt_path = resource_path("prompts/code.txt")
analysis_prompt_path = resource_path("prompts/analyze.txt")

with open(analysis_prompt_path, encoding="utf-8") as f:
    ANALYSIS_SYSTEM_PROMPT = f.read()

with open(code_prompt_path, encoding="utf-8") as f:
    CODE_SYSTEM_PROMPT = f.read()


def formatInput(problem: str) -> str:
    return f"Problem: {problem.strip()}"


def extract_json_safe(text: str) -> dict:
    """
    Extract JSON object from Gemini response safely.
    Handles multi-line JSON and stray text outside braces.
    """
    if not text or not text.strip():
        raise ValueError("Empty response from Gemini")

    # Remove possible code fences
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines)

    # Try to find JSON from first '{' to last '}'
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == -1:
        raise ValueError(f"No JSON found in response:\n{text}")

    json_str = text[start:end]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Attempt to fix common issues: replace unescaped newlines
        cleaned = json_str.replace("\n", "\\n").replace("\r", "")
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON:\n{json_str}")


# Reuse a single client
client = genai.Client(api_key=GEMINI_API_KEY)


def getResponseFromGemini(problem: str, system_prompt: str) -> dict:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {"role": "user", "parts": [{"text": system_prompt + "\n\n" + problem}]}
        ],
    )
    return extract_json_safe(response.text)


def strip_code_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        lines = code.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)
    return code.strip()


def getCode(problem: str, system_prompt: str, language="C++17") -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"{system_prompt}\n\nWrite a complete {language} solution "
                        f"for the following problem. Output ONLY the code. No explanations.\n\n{problem}"
                    }
                ],
            }
        ],
    )
    return strip_code_fences(response.text)


def getProblemFromCF(problem_number: str):
    problem_number = problem_number.strip().upper()
    problem_dict = lookup_or_scrape(problem_number)
    problem_text = f"{problem_number} \nProblem Title: {problem_dict["title"]} \nProblem Statement: {problem_dict["statement"]} \nProblem Inputs: {problem_dict["input"]} \nProblem Outputs: {problem_dict["output"]}"
    return problem_text


def getProblemAnalysis(problem: str):
    problem_text = getProblemFromCF(problem)
    formatted_problem = formatInput(problem_text)
    analysis_response = getResponseFromGemini(formatted_problem, ANALYSIS_SYSTEM_PROMPT)
    code_response = getCode(formatted_problem, CODE_SYSTEM_PROMPT)

    final_response = {"analysis": analysis_response, "code": code_response}

    # Ensure data/cache directories exist
    data_path = resource_path("../data")
    cache_path = resource_path("../data/cache")
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(cache_path, exist_ok=True)

    # Cache individual problem
    cache_file_path = os.path.join(cache_path, f"{problem.strip().lower()}.txt")
    with open(cache_file_path, "w", encoding="utf-8") as file:
        json.dump(final_response, file, indent=4)


def write_solution(write_file_path: str, problem: str):
    cache_path = resource_path("../data/cache")
    cache_file_path = os.path.join(cache_path, f"{problem.strip().lower()}.txt")

    with open(cache_file_path, encoding="utf-8") as file:
        code_solution = json.load(file)["code"]
    with open(write_file_path, "w", encoding="utf-8") as wf:
        wf.write(code_solution)


def getHint(level: int, problem: str) -> str:
    cache_path = resource_path("../data/cache")
    cache_file_path = os.path.join(cache_path, f"{problem.strip().lower()}.txt")

    with open(cache_file_path, encoding="utf-8") as file:
        hints = json.load(file)["analysis"]["hints"]

    return hints.get(f"level{level}", f"Error: No Hint Level Beyond {level}")
