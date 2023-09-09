# api/gradio/gradio_runner.py
import argparse
from .gradio_app import start


def run_gradio():
    parser = argparse.ArgumentParser(description="Start the Gradio App")
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()

    start(debug=args.debug)


if __name__ == '__main__':
    run_gradio()
