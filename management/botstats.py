from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.db import sqlite_conn
from utils import readable_time
from utils.decorators import description, example, triggers, usage

from pymongo import MongoClient
from config.options import config

password = config["TELEGRAM"]["MONGODB_PWD"]
connection_string = f"mongodb+srv://billgateokoye:{password}@cluster0.3ver0qh.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)

telegram_db = client.telegram_bot
collections = telegram_db.timestamp


@usage("/users")
@example("/users")
@triggers(["users"])
@description("Get number of users that user this bot.")
async def get_total_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM chat_stats;")

    await update.message.reply_text(
        f"@{context.bot.username} is used by <b>{cursor.fetchone()[0]}</b> users.",
        parse_mode=ParseMode.HTML,
    )


@usage("/groups")
@example("/groups")
@triggers(["groups"])
@description("Get number of groups that use bot.")
async def get_total_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT chat_id) FROM chat_stats;")

    await update.message.reply_text(
        f"@{context.bot.username} is used in <b>{cursor.fetchone()[0]}</b> groups.",
        parse_mode=ParseMode.HTML,
    )


@usage("/uptime")
@example("/uptime")
@triggers(["uptime"])
@description("Get duration since the bot instance was started.")
async def get_uptime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uptime = collections.find_one({"field": "bot_startup_time"})["value"]
    if not uptime:
        await update.message.reply_text("This bot has not been started yet.")
        return

    uptime = int(float(uptime))
    await update.message.reply_text(
        f"@{context.bot.username} has been online for <b>{await readable_time(uptime)}</b>.",
        parse_mode=ParseMode.HTML,
    )


@usage("/botstats")
@example("/botstats")
@triggers(["botstats"])
@description("Get usage stats of all bot commands.")
async def get_command_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor = sqlite_conn.cursor()
    cursor.execute(
        """
        SELECT *, COUNT(id) AS command_count
        FROM command_stats
        GROUP BY command
        ORDER BY COUNT(id) DESC
        LIMIT 10;
        """,
    )

    text = f"Stats for <b>@{context.bot.username}:</b>\n\n"

    rows = cursor.fetchall()
    cursor.execute(
        """
        SELECT id FROM main.command_stats ORDER BY id DESC LIMIT 1;
        """
    )

    total_count = cursor.fetchone()["id"]

    for row in rows:
        text += f"""<code>{row['command_count']:4} - /{row['command']}</code>\n"""

    text += f"\nTotal: <b>{total_count}</b>"
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
    )
