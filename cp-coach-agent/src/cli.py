from colorama import Fore, Style, init
import argparse

init(autoreset=True)

parser = argparse.ArgumentParser(
    prog="cpcoach", description="Competitive Programming Coach Agent"
)
subparsers = parser.add_subparsers(dest="command")


analyze_parser = subparsers.add_parser("analyze", help="Analyze a problem")

group = analyze_parser.add_mutually_exclusive_group(required=True)
group.add_argument("problem_number", nargs="?", help="Problem number e.g. 116A, 267G")
group.add_argument("-t", "--text", type=str, metavar='"TEXT"', help="Text input mode")


hint_parser = subparsers.add_parser("hint", help="Give a hint")
hint_parser.add_argument("--level1", "-l1", action="store_true", help="Hint Level One")
hint_parser.add_argument("--level2", "-l2", action="store_true", help="Hint Level Two")
hint_parser.add_argument(
    "--level3", "-l3", action="store_true", help="Hint Level Three"
)
hint_parser.add_argument("--level4", "-l4", action="store_true", help="Hint Level Four")
hint_parser.add_argument("--level5", "-l5", action="store_true", help="Hint Level Five")


args = parser.parse_args()


if args.command is None:
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
    print("  analyze  - Analyze a problem number or text")
    print("  hint     - Get hints for problems")

elif args.command == "analyze":
    if args.text:
        print(Fore.GREEN + f"[ANALYZE] Running in text mode: {args.text}")
    else:
        print(Fore.BLUE + f"[ANALYZE] Problem number: {args.problem_number}")

elif args.command == "hint":
    if args.level1:
        print(Fore.YELLOW + "[HINT] Level One hint")
    elif args.level2:
        print(Fore.YELLOW + "[HINT] Level Two hint")
    elif args.level3:
        print(Fore.YELLOW + "[HINT] Level Three hint")
    elif args.level4:
        print(Fore.YELLOW + "[HINT] Level Four hint")
    elif args.level5:
        print(Fore.YELLOW + "[HINT] Level Five hint")
    else:
        print(
            Fore.RED
            + "[HINT] No level selected, choose --level1, --level2, --level3, --level4, --level5"
        )

else:
    parser.print_help()
