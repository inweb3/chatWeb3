import argparse
from api.gradio.gradio_app import start as gradio_start
from api.fastapi import start as fastapi_start
from config.logging_config import initialize_root_logger


def main():
    parser = argparse.ArgumentParser(description="Start ChatWeb3 interfaces")
    parser.add_argument(
        "--interface",
        choices=["gradio", "fastapi"],
        default="gradio",
        help="Choose the interface to run (default: gradio)",
    )

    args = parser.parse_args()

    if args.interface == "gradio":
        gradio_start()
    elif args.interface == "fastapi":
        fastapi_start()


if __name__ == "__main__":
    initialize_root_logger()
    main()
