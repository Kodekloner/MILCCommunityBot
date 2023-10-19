from datetime import datetime
from typing import Optional

from telegram.error import BadRequest
from telegram.ext import ContextTypes

from pymongo import MongoClient
from config.options import config

password = config["TELEGRAM"]["MONGODB_PWD"]
connection_string = f"mongodb+srv://billgateokoye:{password}@cluster0.3ver0qh.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)

telegram_db = client.telegram_bot
user = telegram_db.users


async def readable_time(input_timestamp: int) -> str:
    """
    Return a readable time string.
    """
    seconds = abs(round(datetime.now().timestamp()) - input_timestamp)

    if seconds < 60:
        return "{0:.1f} second".format(seconds).rstrip("0").rstrip(".") + (
            "s" if seconds > 1 else ""
        )
    elif seconds < 3600:
        minutes = seconds / 60
        return "{0:.1f} minute".format(minutes).rstrip("0").rstrip(".") + (
            "s" if minutes > 1 else ""
        )
    elif seconds < 86400:
        hours = seconds / 3600
        return "{0:.1f} hour".format(hours).rstrip("0").rstrip(".") + (
            "s" if hours > 1 else ""
        )
    elif seconds < 604800:
        days = seconds / 86400
        return "{0:.1f} day".format(days).rstrip("0").rstrip(".") + (
            "s" if days > 1 else ""
        )
    elif seconds < 31536000:
        weeks = seconds / 604800
        return "{0:.1f} week".format(weeks).rstrip("0").rstrip(".") + (
            "s" if weeks > 1 else ""
        )
    else:
        years = seconds / 31536000
        return "{0:.1f} year".format(years).rstrip("0").rstrip(".") + (
            "s" if years > 1 else ""
        )


async def get_username(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get the username and/or first_name for a user_id.
    """
    username = user.find_one({"field": f"user_id:{user_id}"})["value"]
    if username:
        return username
    else:
        chat = await context.bot.get_chat(user_id)
        if chat.username:
            user.insert_one({"field": f"user_id:{user_id}", "value": chat.username})
            return chat.username
        elif chat.first_name:
            return chat.first_name
        else:
            return f"{user_id}"


async def get_first_name(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get the first_name for a user_id.
    """
    try:
        chat = await context.bot.get_chat(user_id)
    except BadRequest:
        return f"{user_id}"

    return chat.first_name


async def get_user_id_from_username(username: str) -> Optional[int]:
    """
    Get the user_id from a username.
    """
    user_id = user.find_one({"field": f"username:{username.replace('@', '')}"})["value"]
    return int(user_id) if user_id else None
