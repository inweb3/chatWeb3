# ChatWeb3 - ChatGPT for blockchain and crypto data analysis

More details about this application prototype is available at: 

**[Can ChatGPT unlock blockchain data for the masses? Early insights from building ChatWeb3](https://www.inweb3.com/chatcrypto-chatgpt-for-blockchain-data/)**

## Required API keys

### Flipsidecrypto database

Create a `.env` file and add a Flipside API key, which allows the application to query the Flipsidecrypto database. Flipside API key can be obtained [here](https://flipsidecrypto.xyz/account/api-keys), and it has a free tier as well.

```
FLIPSIDE_API_KEY="XXX"
```

### OpenAI chatGPT

You will need to provide your OpenAI API key to use this application. An OpenAI API key can be obtained from [Openai](https://platform.openai.com/account/api-keys). 

## Installation

```
git clone https://github.com/inWeb3ai/chatWeb3.git
cd chatWeb3
poetry shell
poetry install
```

## Run the application

```
poetry run chatweb3
```

This command will run the ChatWeb3 gradio app. If you prefer to run it as a fastapi service, you can use:

```
poetry run chatweb3 --interface fastapi
```

## Test

To run tests:

```
make test
make integration_tests
```

## Development

General configuration can be done through `config/config.yaml`

To enable detailed log, set the log_level to `logging.DEBUG` in `logger_callback.py`.

```
logger = get_logger(
    __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
)
```

The log file is located under the `chatweb3/logs` directory.