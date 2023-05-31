# chatweb3 - ChatGPT for blockchain and crypto data analysis

More details about this application prototype is available at: 

**[Can ChatGPT unlock blockchain data for the masses? Early insights from building ChatWeb3](https://www.inweb3.com/chatcrypto-chatgpt-for-blockchain-data/)**

## Install the requirements

Using pip:

```
pip install -r requirements.txt
```

## Required API keys

### Flipsidecrypto database

Create a `.env` file and add a ShroomDK API key, which allows the application to query the Flipsidecrypto database. ShroomDK API key can be obtained [here](https://sdk.flipsidecrypto.xyz/shroomdk).

```
SHROOMDK_API_KEY="XXX"
```

### OpenAI chatGPT

You will need to provide your OpenAI API key to use this application. An OpenAI API key can be obtained from [Openai](https://platform.openai.com/account/api-keys). 

## Run the application

```
python chat_ui.py 
```

## Test

To run tests:

```
make test
make integration_tests
```

## Development

General configuration can be done through `config/config.yaml`

Conversational chat agent can be enabled by setting the `CONVERSATIOn_MODE` to 'TRUE' in `chat_ui.py`.

To enable detailed log, set the log_level to `logging.DEBUG` in `logger_callback.py`.

```
logger = get_logger(
    __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
)
```
