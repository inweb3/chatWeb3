import argparse

from dotenv import load_dotenv

from config.logging_config import initialize_root_logger

load_dotenv()


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
        from api.gradio.gradio_app import start as gradio_start

        gradio_start()
    elif args.interface == "fastapi":
        from api.api_endpoints import start as fastapi_start

        fastapi_start()


if __name__ == "__main__":
    initialize_root_logger()
    main()
