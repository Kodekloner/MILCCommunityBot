import datetime
import html
import json
import os
import traceback

from pymongo import MongoClient
from typing import Dict, Optional, Tuple

from telegram import Chat, ChatMember, ChatMemberUpdated, Update
from telegram.constants import ParseMode
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    PicklePersistence,
)

import commands
from config.logger import logger
from config.options import config
from config.db import sqlite_conn
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


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member

# tracks when the bot is added or removed, blocked or unblocked
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    cursor = sqlite_conn.cursor()

    result = extract_status_change(update.my_chat_member)
    print(result)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name
    cause_name_id = update.effective_user.id
    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            # This may not be really needed in practice because most clients will automatically
            # send a /start command after the user unblocks the bot, and start_private_chat()
            # will add the user to "user_ids".
            # We're including this here for the sake of the example.
            logger.info("%s unblocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
            cursor.execute(
                f"INSERT INTO chat_stats (chat_id, user_id, title, type) VALUES (?, ?, ?, ?)",
                (chat.id, cause_name_id, chat.title, chat.type),
            )
            sqlite_conn.commit()
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
            cursor.execute("DELETE FROM chat_stats WHERE chat_id = ?;", (chat.id,),)
            sqlite_conn.commit()
    elif not was_member and is_member:
        logger.info("%s added the bot to the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).add(chat.id)
        cursor.execute(
            f"INSERT INTO chat_stats (chat_id, user_id, title, type) VALUES (?, ?, ?, ?)",
            (chat.id, cause_name_id, chat.title, chat.type),
        )
        sqlite_conn.commit()
    elif was_member and not is_member:
        logger.info("%s removed the bot from the channel %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)
        cursor.execute("DELETE FROM chat_stats WHERE chat_id = ?;", (chat.id,),)
        sqlite_conn.commit()


async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets new users in chats and announces when someone leaves"""
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    cursor = sqlite_conn.cursor()
    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()
    chat = update.chat_member.chat
    member = update.chat_member.new_chat_member.user

    if not was_member and is_member:
        cursor.execute("SELECT * FROM user_wallet_twitter")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                if int(row['userid']) == int(member.id):
                    cursor.execute("UPDATE user_wallet_twitter SET chat_id = ?, telegram_group = ? WHERE userid = ?", (chat.id, chat.title, member.id))
                    sqlite_conn.commit()
        await update.effective_chat.send_message(
            f"{member_name} was added by {cause_name}. Welcome!",
            parse_mode=ParseMode.HTML,
        )

    elif was_member and not is_member:
        cursor.execute("DELETE FROM user_wallet_twitter WHERE userid = ?;", (member.id,),)
        sqlite_conn.commit()
        await update.effective_chat.send_message(
            f"{member_name} is no longer with us. Thanks a lot, {cause_name} ...",
            parse_mode=ParseMode.HTML,
        )


def main():
    persistence = PicklePersistence(filepath="conversation_states")
    application = (
        ApplicationBuilder()
        .token(config["TELEGRAM"]["TOKEN"])
        .rate_limiter(AIORateLimiter(max_retries=10))
        .concurrent_updates(True)
        .post_init(post_init)
        .persistence(persistence)
        .build()
    )

    application.add_error_handler(error_handler)

    # Keep track of which chats the bot is in
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))

    # Handle members joining/leaving chats.
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))

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
        # application.run_polling(drop_pending_updates=True)
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
