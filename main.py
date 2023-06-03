import datetime
import html
import json
import os
import traceback

from pymongo import MongoClient
from typing import Dict

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    ContextTypes,
    # PicklePersistence,
)

import commands
from config.logger import logger
from config.options import config
from core.handlers import base_conversation_handler

password = config["TELEGRAM"]["MONGODB_PWD"]
connection_string = f"mongodb+srv://billgateokoye:{password}@cluster0.3ver0qh.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)

telegram_db = client.telegram_bot


async def post_init(application: Application) -> None:
    """
    Initialise the bot.
    """
    logger.info(f"Started @{application.bot.username} (ID: {application.bot.id})")
    collections = telegram_db.timestamp
    collections.insert_one({"field": "bot_startup_time", "value": datetime.datetime.now().timestamp()})

    if (
        "LOGGING_CHANNEL_ID" in config["TELEGRAM"]
        and config["TELEGRAM"]["LOGGING_CHANNEL_ID"]
    ):
        logger.info(
            f"Logging to channel ID: {config['TELEGRAM']['LOGGING_CHANNEL_ID']}"
        )

        await application.bot.send_message(
            chat_id=config["TELEGRAM"]["LOGGING_CHANNEL_ID"],
            text=f"📝 Started @{application.bot.username} (ID: {application.bot.id}) at {datetime.datetime.now()}",
        )

    # Set commands for bot instance
    # await application.bot.set_my_commands(
    #     [
    #         (command.triggers[0], command.description)
    #         for command in commands.list_of_commands
    #     ]
    # )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096-character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update:\n\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>{html.escape(''.join([tb_list[-1], tb_list[-2]]))}</pre>"
    )

    if (
        "LOGGING_CHANNEL_ID" in config["TELEGRAM"]
        and config["TELEGRAM"]["LOGGING_CHANNEL_ID"]
    ):
        # Finally, send the message
        await context.bot.send_message(
            chat_id=config["TELEGRAM"]["LOGGING_CHANNEL_ID"],
            text=message,
            parse_mode=ParseMode.HTML,
        )

def main():
    # persistence = PicklePersistence(filepath="conversation states")
    application = (
        ApplicationBuilder()
        .token(config["TELEGRAM"]["TOKEN"])
        .rate_limiter(AIORateLimiter(max_retries=10))
        .concurrent_updates(True)
        .post_init(post_init)
        # .persistence(persistence)
        .build()
    )

    application.add_error_handler(error_handler)

    application.add_handler(base_conversation_handler())

    if "UPDATER" in config["TELEGRAM"] and config["TELEGRAM"]["UPDATER"] == "webhook":
        logger.info(f"Using webhook URL: {config['TELEGRAM']['WEBHOOK_URL']}")
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", "443")),
            url_path=config["TELEGRAM"]["TOKEN"],
            webhook_url=config["TELEGRAM"]["WEBHOOK_URL"],
        )
    else:
        logger.info("Using polling...")
        application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()