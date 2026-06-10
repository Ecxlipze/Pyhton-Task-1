import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Simple Python automation tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    start_command = subparsers.add_parser("start")
    start_command.add_argument("--config", required=True)
    list_command = subparsers.add_parser("list")
    list_command.add_argument("--config", required=True)
    subparsers.add_parser("stop")

    return parser.parse_args()
