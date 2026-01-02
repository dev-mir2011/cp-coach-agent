import os
import sys
import json
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")


def resource_path(relative_path):
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


def extract_json(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty response from Gemini")

    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"```[a-zA-Z]*", "", text)
        text = text.replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response:\n{text}")

    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON:\n{match.group()}") from e


def strip_code_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        lines = code.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)
    return code.strip()


def getResponseFromGemini(problem: str, system_prompt: str) -> dict:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {"role": "user", "parts": [{"text": system_prompt + "\n\n" + problem}]}
        ],
    )
    return extract_json(response.text)


def getCode(problem: str, system_prompt: str, language="C++17"):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": f"{system_prompt}\n\nWrite a complete {language} solution for the following problem. Output ONLY the code. No explanations.\n\n{problem}"
                    }
                ],
            }
        ],
    )
    return strip_code_fences(response.text)


def getProblemAnalysis(problem: str, problem_text: str):
    formatted_problem = formatInput(problem_text)
    analysis_response = getResponseFromGemini(formatted_problem, ANALYSIS_SYSTEM_PROMPT)
    code_response = getCode(formatted_problem, CODE_SYSTEM_PROMPT)

    final_response = {"analysis": analysis_response, "code": code_response}

    data_path = resource_path("../data")
    cache_path = resource_path("../data/cache")
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(cache_path, exist_ok=True)

    response_json_path = os.path.join(data_path, "response.json")
    with open(response_json_path, "w", encoding="utf-8") as file:
        json.dump(final_response, file, indent=4)

    cache_file_path = os.path.join(cache_path, f"{problem.strip().lower()}.txt")
    with open(cache_file_path, "w", encoding="utf-8") as file:
        json.dump(final_response, file, indent=4)


def getProblemFromCache(path: str):
    with open(path, "r", encoding="utf-8") as rf:
        data = json.load(rf)

    # Root data folder
    data_path = resource_path("../data")
    os.makedirs(data_path, exist_ok=True)

    response_json_path = os.path.join(data_path, "response.json")
    with open(response_json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
