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
        "ADMINS": os.environ.get("ADMINS", os.getenv("ADMINS")).split(" "),
        "TOKEN": os.environ.get("TELEGRAM_TOKEN", os.getenv("TELEGRAM_TOKEN")),
        "UPDATER": os.environ.get("UPDATER", os.getenv("UPDATER")),
        "WEBHOOK_URL": f"""{os.environ.get("WEBHOOK_URL", os.getenv("WEBHOOK_URL"))}/{os.environ.get("TELEGRAM_TOKEN", os.getenv("TELEGRAM_TOKEN"))}""",
        "LOGGING_CHANNEL_ID": int(os.environ.get("LOGGING_CHANNEL_ID"))
        if os.environ.get("LOGGING_CHANNEL_ID")
        else None,
        "QUOTE_CHANNEL_ID": int(os.environ.get("QUOTE_CHANNEL_ID"))
        if os.environ.get("QUOTE_CHANNEL_ID")
        else None,
        "MONGODB_PWD": os.environ.get("MONGODB_PWD", os.getenv("MONGODB_PWD")),
        "BINANCE_API_KEY": os.environ.get("BINANCE_API_KEY", os.getenv("BINANCE_API_KEY")),
        "BINANCE_SECRET_KEY": os.environ.get("BINANCE_SECRET_KEY", os.getenv("BINANCE_SECRET_KEY"))
    },
    "API": {
        "GIPHY_API_KEY": os.environ.get("GIPHY_API_KEY", ""),
        "GOODREADS_API_KEY": os.environ.get("GOODREADS_API_KEY", ""),
        "IMGUR_API_KEY": os.environ.get("IMGUR_API_KEY", ""),
        "INSTAGRAM_SESSION_NAME": os.environ.get("INSTAGRAM_SESSION_NAME", ""),
        "REDDIT": {
            "CLIENT_ID": os.environ.get("REDDIT_CLIENT_ID", ""),
            "CLIENT_SECRET": os.environ.get("REDDIT_CLIENT_SECRET", ""),
            "USER_AGENT": os.environ.get("REDDIT_USER_AGENT", ""),
        },
        "RAPID_API_KEY": os.environ.get("RAPID_API_KEY", ""),
        "SMMRY_API_KEY": os.environ.get("SMMRY_API_KEY", ""),
        "STEAM_API_KEY": os.environ.get("STEAM_API_KEY", ""),
        "TWITTER_BEARER_TOKEN": os.environ.get("TWITTER_BEARER_TOKEN", ""),
        "TWITTER_ACCESS_TOKEN": os.environ.get("TWITTER_ACCESS_TOKEN", os.getenv("TWITTER_ACCESS_TOKEN")),
        "TWITTER_ACCESS_TOKEN_SECRET": os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", os.getenv("TWITTER_ACCESS_TOKEN_SECRET")),
        "TWITTER_API_KEY": os.environ.get("TWITTER_API_KEY", os.getenv("TWITTER_API_KEY")),
        "TWITTER_KEY_SECRET": os.environ.get("TWITTER_KEY_SECRET", os.getenv("TWITTER_KEY_SECRET")),
        "OPEN_AI_API_KEY": os.environ.get("OPEN_AI_API_KEY", ""),
        "WOLFRAM_APP_ID": os.environ.get("WOLFRAM_APP_ID", ""),
        "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY", ""),
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
