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
            "QUOTE_CHANNEL_ID": {
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
            "GIPHY_API_KEY": {
                "type": "string",
                "required": False,
            },
            "GOODREADS_API_KEY": {
                "type": "string",
                "required": False,
            },
            "SMMRY_API_KEY": {
                "type": "string",
                "required": False,
            },
            "STEAM_API_KEY": {
                "type": "string",
                "required": False,
            },
            "WOLFRAM_APP_ID": {
                "type": "string",
                "required": False,
            },
            "INSTAGRAM_SESSION_NAME": {
                "type": "string",
                "required": False,
            },
            "IMGUR_API_KEY": {
                "type": "string",
                "required": False,
            },
            "OPEN_AI_API_KEY": {
                "type": "string",
                "required": False,
            },
            "YOUTUBE_API_KEY": {
                "type": "string",
                "required": False,
            },
            "REDDIT": {
                "type": "dict",
                "schema": {
                    "CLIENT_ID": {
                        "type": "string",
                        "required": False,
                    },
                    "CLIENT_SECRET": {
                        "type": "string",
                        "required": False,
                    },
                    "USER_AGENT": {
                        "type": "string",
                        "required": False,
                    },
                },
            },
            "RAPID_API_KEY": {
                "type": "string",
                "required": False,
            },
            "TWITTER_BEARER_TOKEN": {
                "type": "string",
                "required": False,
            },
        },
    },
}

config = {
    "TELEGRAM": {
        "ADMINS": os.getenv("ADMINS", "").split(" "),
        "TOKEN": os.getenv("TELEGRAM_TOKEN"),
        "UPDATER": os.getenv("UPDATER"),
        "WEBHOOK_URL": f"""{os.getenv("WEBHOOK_URL")}/{os.getenv("TELEGRAM_TOKEN")}""",
        "LOGGING_CHANNEL_ID": int(os.getenv("LOGGING_CHANNEL_ID"))
        if os.getenv("LOGGING_CHANNEL_ID")
        else None,
        "QUOTE_CHANNEL_ID": int(os.getenv("QUOTE_CHANNEL_ID"))
        if os.getenv("QUOTE_CHANNEL_ID")
        else None,
        "MONGODB_PWD": os.getenv("MONGODB_PWD"),
        "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY"),
        "BINANCE_SECRET_KEY": os.getenv("BINANCE_SECRET_KEY")
    },
    "API": {
        "GIPHY_API_KEY": os.getenv("GIPHY_API_KEY", ""),
        "GOODREADS_API_KEY": os.getenv("GOODREADS_API_KEY", ""),
        "IMGUR_API_KEY": os.getenv("IMGUR_API_KEY", ""),
        "INSTAGRAM_SESSION_NAME": os.getenv("INSTAGRAM_SESSION_NAME", ""),
        "REDDIT": {
            "CLIENT_ID": os.getenv("REDDIT_CLIENT_ID", ""),
            "CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET", ""),
            "USER_AGENT": os.getenv("REDDIT_USER_AGENT", ""),
        },
        "RAPID_API_KEY": os.getenv("RAPID_API_KEY", ""),
        "SMMRY_API_KEY": os.getenv("SMMRY_API_KEY", ""),
        "STEAM_API_KEY": os.getenv("STEAM_API_KEY", ""),
        "TWITTER_BEARER_TOKEN": os.getenv("TWITTER_BEARER_TOKEN", ""),
        "OPEN_AI_API_KEY": os.getenv("OPEN_AI_API_KEY", ""),
        "WOLFRAM_APP_ID": os.getenv("WOLFRAM_APP_ID", ""),
        "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY", ""),
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
