from datetime import datetime

from telegram import Message, Update, Chat
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import commands
import utils.string
from config.db import sqlite_conn
from logging import getLogger


from pymongo import MongoClient
from config.options import config

password = config["TELEGRAM"]["MONGODB_PWD"]
connection_string = f"mongodb+srv://billgateokoye:{password}@cluster0.3ver0qh.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)

telegram_db = client.telegram_bot
user = telegram_db.users


# Init logger
logger = getLogger(__name__)

async def increment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Increment message count for a user. Also store last seen time in Redis.
    """
    if not update.message:
        return

    title = update.message.chat.title
    chat_type = update.message.chat.type
    chat_id = update.message.chat.id
    user_object = update.message.from_user

    cursor = sqlite_conn.cursor()
    cursor.execute(
        f"INSERT INTO chat_stats (chat_id, user_id, title, type) VALUES (?, ?, ?, ?)",
        (chat_id, user_object.id, title, chat_type),
    )
