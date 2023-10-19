import os
from dotenv import load_dotenv

from cerberus import Validator

from utils import cleaner
from config.logger import logger

# Load environment variables from .env file
load_dotenv()

schema = {
    "TELEGRAM": {
        "type": "dict",
        "schema": {
            "ADMINS": {
                "type": "list",
                "required": False,
                "default": [],
            },
            "TOKEN": {
                "type": "string",
                "required": True,
            },
            "UPDATER": {
                "type": "string",
                "required": False,
                "allowed": ["webhook", "polling"],
                "default": "polling",
            },
            "WEBHOOK_URL": {
                "type": "string",
                "required": False,
            },
            "LOGGING_CHANNEL_ID": {
                "type": "integer",
                "required": False,
                "nullable": True,
            },
            "MONGODB_PWD": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
        },
    },
    "API": {
        "type": "dict",
        "schema": {
            "TWITTER_BEARER_TOKEN": {
                "type": "string",
                "required": False,
            },
        },
    },
}

config = {
    "TELEGRAM": {
        "ADMINS": os.environ.get("ADMINS", os.getenv("ADMINS")).split(" "),
        "TOKEN": os.environ.get("TELEGRAM_TOKEN", os.getenv("TELEGRAM_TOKEN")),
        "UPDATER": os.environ.get("UPDATER", os.getenv("UPDATER")),
        "WEBHOOK_URL": f"""{os.environ.get("WEBHOOK_URL", os.getenv("WEBHOOK_URL"))}/{os.environ.get("TELEGRAM_TOKEN", os.getenv("TELEGRAM_TOKEN"))}""",
        "LOGGING_CHANNEL_ID": int(os.environ.get("LOGGING_CHANNEL_ID", os.getenv("LOGGING_CHANNEL_ID")))
        if os.environ.get("LOGGING_CHANNEL_ID")
        else None,
        "MONGODB_PWD": os.environ.get("MONGODB_PWD", os.getenv("MONGODB_PWD")),
    },
    "API": {
        "TWITTER_BEARER_TOKEN": os.environ.get("TWITTER_BEARER_TOKEN", ""),
        "TWITTER_ACCESS_TOKEN": os.environ.get("TWITTER_ACCESS_TOKEN", os.getenv("TWITTER_ACCESS_TOKEN")),
        "TWITTER_ACCESS_TOKEN_SECRET": os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", os.getenv("TWITTER_ACCESS_TOKEN_SECRET")),
        "TWITTER_API_KEY": os.environ.get("TWITTER_API_KEY", os.getenv("TWITTER_API_KEY")),
        "TWITTER_KEY_SECRET": os.environ.get("TWITTER_KEY_SECRET", os.getenv("TWITTER_KEY_SECRET")),
    },
}

v = Validator(schema)
v.allow_unknown = True

if v.validate(config):
    logger.info("Valid configuration found.")
    config = cleaner.scrub_dict(config)
    logger.info(config)
else:
    logger.error("Invalid configuration found.")
    logger.error(v.errors)
    exit(1)
