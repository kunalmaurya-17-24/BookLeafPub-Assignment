import sys
import argparse
from agent import run_customer_bot


PURPLE = "\033[95m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner():
    print(f"""
{PURPLE}{BOLD}╔══════════════════════════════════════════════════╗
║           📚  BookLeaf AI Agent  📚              ║
║      AI Automation Specialist — Chat CLI         ║
╚══════════════════════════════════════════════════╝{RESET}
""")

def print_bot(text):
    print(f"\n{GREEN}{BOLD}📚 BookLeaf:{RESET} {GREEN}{text}{RESET}\n")

def print_info(text):
    print(f"{DIM}{text}{RESET}")

def main():
    parser = argparse.ArgumentParser(description="BookLeaf AI Chat CLI")
    parser.add_argument("--platform", default="web", choices=["web", "whatsapp", "instagram", "email"])
    parser.add_argument("--sender", default="cli_user", help="Your handle, phone, or email")
    args = parser.parse_args()

    print_banner()
    print_info(f"  Platform: {args.platform} | Sender: {args.sender}")
    thread_id = f"{args.platform}_{args.sender}"
    print_info(f"  Type your query and press Enter. Type 'quit' or 'exit' to leave.\n")
    print(f"{DIM}{'─' * 52}{RESET}")

    while True:
        try:
            query = input(f"\n{CYAN}{BOLD}You ❯ {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{YELLOW}Goodbye!{RESET}")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print(f"\n{YELLOW}Goodbye!{RESET}")
            break

        print(f"{DIM}  Thinking...{RESET}", end="", flush=True)
        try:
            response = run_customer_bot(query, args.platform, args.sender, thread_id=thread_id)
            print(f"\r{' ' * 20}\r", end="")  
            print_bot(response)
        except Exception as e:
            print(f"\r{' ' * 20}\r", end="")
            print(f"\n{YELLOW}⚠ Error: {e}{RESET}\n")

if __name__ == "__main__":
    main()
