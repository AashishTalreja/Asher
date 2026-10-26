"""
Bihar Cyber Fraud Investigation Platform - Main Entry Point (main.py)

Launches the Rich + prompt_toolkit Terminal UI Application.
Supports:
  - Main interactive dashboard (8 screens)
  - Account direct inspection: python main.py ACC-22451
  - Projector / plain ASCII fallback: python main.py --fallback
"""

import sys
from cli.app import CLIApp


def main():
    fallback_flag = "--fallback" in sys.argv or "--no-color" in sys.argv or "--ascii" in sys.argv
    data_dir = "data"
    for i, arg in enumerate(sys.argv):
        if arg == "--data-dir" and i + 1 < len(sys.argv):
            data_dir = sys.argv[i + 1]

    # Initialize CLI app
    app = CLIApp(data_dir=data_dir, fallback=fallback_flag)

    # Direct account inspection or standard interactive app
    for arg in sys.argv[1:]:
        if arg.upper().startswith("ACC-"):
            app.screen_account_360(arg.upper())
            return

    # Start main interactive menu loop
    app.run()


if __name__ == "__main__":
    main()
