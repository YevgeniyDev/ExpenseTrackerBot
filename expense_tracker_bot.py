import logging
import logging.config
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def setup_logging(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
        logging.config.dictConfig(config)

if __name__ == "__main__":
    # Load logging configuration
    setup_logging('logging_config.json')

    # Your main bot logic here
    # ...
