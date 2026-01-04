from colorama import Fore, Style, init
import argparse
import os
from pathlib import Path
import time

from utils import (
    getProblemAnalysis,
    resource_path,
    getHint,
    write_solution,
)

from pdf import generate_pdf_report
from dotenv import load_dotenv

init(autoreset=True)

parser = argparse.ArgumentParser(
    prog="cpcoach",
    description="Competitive Programming Coach Agent",
)

subparsers = parser.add_subparsers(dest="command", required=False)

# --- Analyze Command ---
analyze_parser = subparsers.add_parser(
    "analyze",
    help="Analyze a problem using a problem number and file",
)
analyze_parser.add_argument(
    "problem_number",
    help="Problem number (e.g. 116A, 267G)",
)

# --- Hint Command ---
hint_parser = subparsers.add_parser("hint", help="Give a hint")
hint_parser.add_argument("problem_number", help="Problem number (e.g. 116A, 267G)")
hint_parser.add_argument("--level1", "-l1", action="store_true")
hint_parser.add_argument("--level2", "-l2", action="store_true")
hint_parser.add_argument("--level3", "-l3", action="store_true")
hint_parser.add_argument("--level4", "-l4", action="store_true")
hint_parser.add_argument("--level5", "-l5", action="store_true")

# --- Solution Command ---
solution_parser = subparsers.add_parser("solution", help="Generate solution from file")
solution_parser.add_argument("problem_number", help="Problem number (e.g. 116A, 267G)")
solution_parser.add_argument(
    "--file",
    "-f",
    required=True,
    help="Path to file containing the problem statement",
)

# --- PDF Report Command ---
pdf_parser = subparsers.add_parser("report", help="Generate PDF report for a problem")
pdf_parser.add_argument("problem_number", help="Problem number (e.g. 116A, 267G)")
pdf_parser.add_argument("-l", "--light", action="store_true", help="Light theme")
pdf_parser.add_argument("-d", "--dark", action="store_true", help="Dark theme")
pdf_parser.add_argument("-p", "--print", action="store_true", help="Print theme")
pdf_parser.add_argument("-o", "--open", action="store_true", help="Auto-open PDF")

# --- Setup Command ---
setup_parser = subparsers.add_parser("setup", help="Set your API key")
setup_parser.add_argument("api_key", help="Your API key for CPCoach")

# --- Doctor Command ---
doctor_parser = subparsers.add_parser(
    "doctor", help="Check system status (API key, cache, env)"
)

args = parser.parse_args()


def print_banner():
    print(
        Fore.GREEN
        + r"""
   ██████╗██████╗  ██████╗ ██████╗  ██████╗  ██████╗██╗  ██╗
  ██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔═══██╗██╔════╝██║  ██║
  ██║     ██████╔╝██║     ██║   ██║███████║██║     ███████║
  ██║     ██╔═══╝ ██║     ██║   ██║██╔══██║██║     ██╔══██║
  ╚██████╗██║     ╚██████╗╚██████╔╝██║  ██║╚██████╗██║  ██║
   ╚═════╝╚═╝      ╚═════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
                                                              
       ▀▀▀▀▀  COMPETITIVE PROGRAMMING COACH AGENT  ▀▀▀▀▀
"""
        + Style.RESET_ALL
    )


if args.command is None:
    print_banner()
    print("Available Commands:")
    print("  analyze   - Analyze a problem using a file")
    print("  hint      - Get hints for problems")
    print("  solution  - Generate solution from file")
    print("  report    - Generate PDF report for a problem")
    print("  setup     - Set your API key")
    print("  doctor    - Check system status (API key, cache, environment)")
    print("\nUse 'cpcoach <command> --help' for more information on a command.")

elif args.command == "analyze":
    print(Fore.BLUE + f"[ANALYZE] Problem Number: {args.problem_number.upper()}")
    time.sleep(1.5)
    print(Fore.GREEN + "[ANALYZE] Loaded problem statement")
    time.sleep(0.5)
    print(Fore.GREEN + "[ANALYZE] Processing....")

    cache_file = Path(
        resource_path(
            f"../data/cache/{args.problem_number.strip().lower().replace(' ', '')}.txt"
        )
    )
    os.makedirs(cache_file.parent, exist_ok=True)

    if cache_file.exists():
        time.sleep(2)
        print(
            Fore.GREEN
            + f"[COMPLETE] Analysis of Problem {args.problem_number.upper()} is Complete.\nYou may ask for a hint or the solution now"
        )
    else:
        getProblemAnalysis(args.problem_number)
        print(
            Fore.GREEN
            + f"[COMPLETE] Analysis of Problem {args.problem_number.upper()} is Complete.\nYou may ask for a hint or the solution now"
        )

elif args.command == "hint":
    if not args.problem_number:
        print(Fore.RED + "[ERROR] Must Enter A Problem Number.")
    else:
        level_found = False
        for i, lvl in enumerate(
            [args.level1, args.level2, args.level3, args.level4, args.level5], start=1
        ):
            if lvl:
                print(Fore.YELLOW + f"[HINT] Level {i}")
                print(
                    Fore.GREEN + f"[HINT-LEVEL-{i}] {getHint(i, args.problem_number)}"
                )
                level_found = True
                break
        if not level_found:
            print(Fore.RED + "[HINT] Select a hint level using -l1 ... -l5")

elif args.command == "solution":
    if not args.problem_number:
        print(Fore.RED + "[ERROR] Must Enter A Problem Number.")
    elif not os.path.isfile(args.file):
        print(Fore.RED + f"[ERROR] File not found: {args.file}")
        exit(1)
    else:
        print(Fore.BLUE + f"[WRITING] Writing Solution To {args.file}....")
        write_solution(args.file, args.problem_number)
        time.sleep(0.75)
        print(Fore.GREEN + f"[SUCCESS] Solution Written To {args.file} !")

elif args.command == "report":
    if not args.problem_number:
        print(Fore.RED + "[ERROR] Must Enter A Problem Number.")
    else:
        print(
            Fore.BLUE
            + f"[GENERATING] Generating PDF report of Problem {args.problem_number.strip().upper()}...."
        )
        time.sleep(0.5)

        theme = "dark"
        if args.light:
            theme = "light"
        elif args.print:
            theme = "print"
        elif args.dark:
            theme = "dark"

        auto_open = args.open
        generate_pdf_report(
            args.problem_number.strip().upper(), theme=theme, auto_open=auto_open
        )

elif args.command == "setup":
    api_key = args.api_key.strip()
    env_path = Path(os.getcwd()) / ".env"
    with open(env_path, "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    print(Fore.GREEN + f"[SETUP] API key written to {env_path}")

elif args.command == "doctor":
    print(Fore.CYAN + "[DOCTOR] Running system diagnostics...\n")

    # Check .env
    env_path = Path(os.getcwd()) / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print(Fore.GREEN + f"[OK] API key found in {env_path}")
        else:
            print(Fore.RED + f"[ERROR] API key not found in {env_path}")
    else:
        print(Fore.RED + f"[ERROR] .env file not found at {env_path}")

    # Check cache folder
    cache_path = Path(resource_path("../data/cache"))
    if cache_path.exists():
        print(Fore.GREEN + f"[OK] Cache folder exists: {cache_path}")
        try:
            test_file = cache_path / ".doctor_test"
            test_file.write_text("test")
            test_file.unlink()
            print(Fore.GREEN + "[OK] Cache folder is writable")
        except Exception as e:
            print(Fore.RED + f"[ERROR] Cache folder not writable: {e}")
    else:
        print(Fore.RED + f"[ERROR] Cache folder does not exist: {cache_path}")

    # Report working directory
    print(Fore.CYAN + f"[INFO] Current working directory: {os.getcwd()}")
    print(Fore.CYAN + "[DOCTOR] Diagnostics complete")
