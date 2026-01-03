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

hint_parser = subparsers.add_parser("hint", help="Give a hint")
hint_parser.add_argument("problem_number", help="Problem number (e.g. 116A, 267G)")
hint_parser.add_argument("--level1", "-l1", action="store_true")
hint_parser.add_argument("--level2", "-l2", action="store_true")
hint_parser.add_argument("--level3", "-l3", action="store_true")
hint_parser.add_argument("--level4", "-l4", action="store_true")
hint_parser.add_argument("--level5", "-l5", action="store_true")

solution_parser = subparsers.add_parser("solution", help="")
solution_parser.add_argument("problem_number", help="Problem number (e.g. 116A, 267G)")
solution_parser.add_argument(
    "--file",
    "-f",
    required=True,
    help="Path to file containing the problem statement",
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
    print("  analyze  - Analyze a problem using a file")
    print("  hint     - Get hints for problems")

elif args.command == "analyze":
    print(Fore.BLUE + f"[ANALYZE] Problem Number: {args.problem_number.upper()}")
    time.sleep(1.5)
    print(Fore.GREEN + "[ANALYZE] Loaded problem statement")
    time.sleep(0.5)
    print(Fore.GREEN + "[ANALYZE] Processing....")

    cache_file = Path(
        resource_path(
            f"../data/cache/{args.problem_number.strip().lower().replace(" ", "")}.txt"
        )
    )

    os.makedirs(cache_file.parent, exist_ok=True)

    if cache_file.exists():
        time.sleep(2)
        print(
            Fore.GREEN
            + f"[COMPLETE] Analysis of Problem Number {args.problem_number.upper()} is Complete.\nYou may ask for a hint or the solution now"
        )
    else:
        getProblemAnalysis(args.problem_number)
        print(
            Fore.GREEN
            + f"[COMPLETE] Analysis of Problem Number {args.problem_number.upper()} is Complete.\nYou may ask for a hint or the solution now"
        )

elif args.command == "hint":
    if args.problem_number is not None:
        if args.level1:
            print(Fore.YELLOW + "[HINT] Level One")
            print(Fore.GREEN + f"[HINT-LEVEL-1] {getHint(1, args.problem_number)}")
        elif args.level2:
            print(Fore.YELLOW + "[HINT] Level Two")
            print(Fore.GREEN + f"[HINT-LEVEL-2] {getHint(2,  args.problem_number)}")
        elif args.level3:
            print(Fore.YELLOW + "[HINT] Level Three")
            print(Fore.GREEN + f"[HINT-LEVEL-3] {getHint(3, args.problem_number)}")
        elif args.level4:
            print(Fore.YELLOW + "[HINT] Level Four")
            print(Fore.GREEN + f"[HINT-LEVEL-4] {getHint(4, args.problem_number)}")
        elif args.level5:
            print(Fore.YELLOW + "[HINT] Level Five")
            print(Fore.GREEN + f"[HINT-LEVEL-5] {getHint(5, args.problem_number)}")
        else:
            print(Fore.RED + "[HINT] Select a hint level")
    else:
        print(Fore.RED + f"[ERROR] Must Enter A Problem Number.")

elif args.command == "solution":
    if args.problem_number is not None:
        if not os.path.isfile(args.file):
            print(Fore.RED + f"[ERROR] File not found: {args.file}")
            exit(1)
        print(Fore.BLUE + f"[WRITING] Writing Solution To {args.file}....")
        write_solution(args.file, args.problem_number)
        time.sleep(0.75)
        print(Fore.GREEN + f"[SUCCESS] Solution Written To {args.file} !")
    else:
        print(Fore.RED + f"[ERROR] Must Enter A Problem Number.")
