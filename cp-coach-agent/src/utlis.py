from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMENI_API_KEY")

with open(r"cp-coach-agent\src\prompts\analyze.txt") as system_prompt:
    SYSTEM_PROMPT = system_prompt.read()


def formatInput(problem: str):
    problem = problem.strip()
    problem = problem.lower()

    return f"Problem: {problem}"


def getResponseFromGemini(problem: str, SYSTEM_PROMPT: str):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [{"text": SYSTEM_PROMPT + "\n\n" + problem}],
            },
        ],
    )

    output = json.dumps(response)

    return output


def getProblemAnalysis(problem):
    formatted_problem = formatInput(problem)
    response = getResponseFromGemini(formatted_problem, SYSTEM_PROMPT)

    if os.path.exists(r"cp-coach-agent\data\response.json"):
        with open(r"cp-coach-agent\data\response.json", "w") as file:
            json.dump(response, file, indent=4)

    else:
        with open(r"cp-coach-agent\data\response.json", "w") as file:
            json.dump(response, file, indent=4)
