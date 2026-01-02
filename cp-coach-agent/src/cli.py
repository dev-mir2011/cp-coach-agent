from colorama import Fore, Style, init
import argparse
import os
from pathlib import Path

from utils import getProblemAnalysis, getProblemFromCache, resource_path

init(autoreset=True)

parser = argparse.ArgumentParser(
    prog="cpcoach",
    description="Competitive Programming Coach Agent",
)

subparsers = parser.add_subparsers(dest="command", required=False)

analyze_parser = subparsers.add_parser(
    "analyze",
    help="Analyze a problem using a problem number and file",
)
analyze_parser.add_argument(
    "problem_number",
    help="Problem number (e.g. 116A, 267G)",
)
analyze_parser.add_argument(
    "-f",
    "--file",
    required=True,
    help="Path to file containing the problem statement",
)

hint_parser = subparsers.add_parser("hint", help="Give a hint")
hint_parser.add_argument("--level1", "-l1", action="store_true")
hint_parser.add_argument("--level2", "-l2", action="store_true")
hint_parser.add_argument("--level3", "-l3", action="store_true")
hint_parser.add_argument("--level4", "-l4", action="store_true")
hint_parser.add_argument("--level5", "-l5", action="store_true")

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
    print("  analyze  - Analyze a problem using a file")
    print("  hint     - Get hints for problems")

elif args.command == "analyze":
    if not os.path.isfile(args.file):
        print(Fore.RED + f"[ERROR] File not found: {args.file}")
        exit(1)

    with open(args.file, "r", encoding="utf-8") as f:
        problem_text = f.read()

    print(Fore.BLUE + f"[ANALYZE] Problem Number: {args.problem_number}")
    print(Fore.GREEN + "[ANALYZE] Loaded problem statement")
    print(Fore.GREEN + "[ANALYZE] Processing....")

    cache_file = Path(
        resource_path(f"../data/cache/{args.problem_number.strip().lower()}.txt")
    )

    os.makedirs(cache_file.parent, exist_ok=True)

    if cache_file.exists():
        getProblemFromCache(cache_file)
    else:
        getProblemAnalysis(args.problem_number, problem_text)

    print(
        Fore.GREEN
        + f"[COMPLETE] Analysis of Problem Number {args.problem_number} is Complete.\nYou may ask for a hint or the solution now"
    )

elif args.command == "hint":
    if args.level1:
        print(Fore.YELLOW + "[HINT] Level One")
    elif args.level2:
        print(Fore.YELLOW + "[HINT] Level Two")
    elif args.level3:
        print(Fore.YELLOW + "[HINT] Level Three")
    elif args.level4:
        print(Fore.YELLOW + "[HINT] Level Four")
    elif args.level5:
        print(Fore.YELLOW + "[HINT] Level Five")
    else:
        print(Fore.RED + "[HINT] Select a hint level")
