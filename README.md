# CPCoach — Competitive Programming Coach Agent

CPCoach is a Python-based CLI tool designed to help competitive programmers analyze problems, get hints, generate reference solutions, and produce PDF reports for competitive programming problems from platforms like Codeforces.

---

## Features

- **Analyze Problems**: Automatically scrape or use cached problem statements and generate detailed analyses.
- **Hints**: Get multi-level hints for solving problems.
- **Solution Generation**: Generate reference solutions for problems in your local files.
- **PDF Reports**: Generate well-formatted reports summarizing problems, strategies, and complexity analyses.
- **Setup CLI**: Easily configure your API key for Gemini AI via `.env`.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/dev-mir2011/cp-coach-agent.git
cd cp-coach-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set your Gemini AI API key:

```bash
cpcoach setup
```

## Usage

### CPCoach provides a simple CLI :-

`cpcoach <command> [options]`

### Commands :-

`analyze <problem_number>`
Analyze a problem and store results in cache.

`hint <problem_number> [--level1 ... --level5]`
Get a hint for a specific level.

`solution <problem_number> --file <file_path>`
Write a reference solution to a file.

`report <problem_number> [--light | --dark | --print] [-o]`
Generate a PDF report. Use -o to automatically open the PDF.

`setup`
Configure your Gemini API key in .env .

## Example

```bash
cpcoach analyze 116A
cpcoach hint 116A --level2
cpcoach solution 116A --file solution.cpp
cpcoach report 116A --dark -o
```

## Requirements

- Python 3.10+

- Dependencies listed in `requirements.txt`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE)
for details.

---
