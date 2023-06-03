# """
# Commands for general use.
# """
# import re
#
# from telegram import Message, MessageEntity, Update
# from telegram.constants import ChatAction, ParseMode
# from telegram.ext import CommandHandler, ContextTypes
#
# from typing import Union, List
#
# import management
# import utils
#
#
# from config import logger
# from config.db import sqlite_conn
# from config.options import config
# # from management.botstats import (
# #     get_command_stats,
# #     get_total_chats,
# #     get_total_users,
# #     get_uptime,
# # )
# # from management.stats import get_chat_stats, get_last_seen, get_total_chat_stats
# # from .animals import animal
# # from .book import book
# # from .calc import calc
# # from .define import define
# # from .gif import gif
# # from .insult import insult
# # from .joke import joke
# # from .meme import meme
# # from .person import person
# # from .pic import pic
# # from .ping import ping
# # from .quote import add_quote, get_quote
# # from .summon import summon, summon_keyboard_button
# # from .tldr import tldr
# # from .transcribe import transcribe
# # from .twitter import search
# # from .cryptoToken import create_wallet
# # from .ud import ud
# from .admin import admin
# from .start import start
# from .privacy import privacy
#
#
# async def disabled(update: Update, _: ContextTypes.DEFAULT_TYPE):
#     """
#     Disabled command handler.
#     """
#     await update.message.reply_text("❌ This command is disabled.")
#
#
# list_of_commands = [
#     admin,
#     start,
#     privacy,
# ]
#
# command_handler_list = []
# command_doc_list = {}
# for command in list_of_commands:
#     if hasattr(command, "api_key"):
#         if command.api_key in config["API"]:
#             handler = command
#         else:
#             handler = disabled
#     else:
#         handler = command
#
#     command_handler_list.append(
#         CommandHandler(
#             command.triggers,
#             handler,
#         )
#     )
#
#     for trigger in command.triggers:
#         command_doc_list[trigger] = {
#             "description": command.description,
#             "usage": command.usage,
#             "example": command.example,
#         }
#
# # async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     query = update.callback_query
# #     if query.data.startswith("rts"):
# #         await tv_show_button(update, context)
# #     elif query.data.startswith("hl"):
# #         await highlight_button_handler(update, context)
# #     elif query.data.startswith("sg"):
# #         await summon_keyboard_button(update, context)
# #     elif query.data.startswith("yt"):
# #         await youtube_button(update, context)
# #     elif query.data.startswith("as"):
# #         await subscribe_show(update, context)
# #     elif query.data.startswith("show_eta"):
# #         await eta_keyboard_builder(update, context)
# #     elif query.data.startswith("hide_eta"):
# #         query = update.callback_query
# #         user_id, chat_id = query.data.replace("hide_eta:", "").split(",")
# #
# #         await context.bot.edit_message_text(
# #             text="List of your shows in this chat. Tap on a show to remove it from your watchlist:",
# #             chat_id=query.message.chat.id,
# #             message_id=query.message.message_id,
# #             reply_markup=await keyboard_builder(user_id, chat_id),
# #         )
# #     elif query.data.startswith("unsubscribe_reddit"):
# #         await reddit_subscription_button_handler(update, context)
# #     else:
# #         await query.answer("No function found for this button.")
#
#
# async def usage_string(message: Message, func) -> None:
#     """
#     Return the usage string for a command.
#     """
#     await message.reply_text(
#         f"{func.description}\n\n<b>Usage:</b>\n<pre>{func.usage}</pre>\n\n<b>Example:</b>\n<pre>{func.example}</pre>",
#         parse_mode=ParseMode.HTML,
#         disable_web_page_preview=True,
#     )
#
#
# # async def save_mentions(
# #     mentioning_user_id: int,
# #     mentioned_users: List[Union[str, int]],
# #     message: Message,
# # ) -> None:
# #     """
# #     Save a mention in the database.
# #     """
# #     for user in mentioned_users:
# #         if isinstance(user, str):
# #             user_id = await utils.get_user_id_from_username(user)
# #         else:
# #             user_id = user
# #
# #         if user_id is not None:
# #             cursor = sqlite_conn.cursor()
# #             cursor.execute(
# #                 """
# #                 INSERT INTO chat_mentions (mentioning_user_id, mentioned_user_id, chat_id, message_id)
# #                 VALUES (?, ?, ?, ?)
# #                 """,
# #                 (mentioning_user_id, user_id, message.chat.id, message.message_id),
# #             )
# #
# #
# # async def increment_command_count(
# #     update: Update, context: ContextTypes.DEFAULT_TYPE
# # ) -> None:
# #     """
# #     Increment command count for a /<command> invocation.
# #     """
# #     sent_command = next(
# #         iter(update.message.parse_entities([MessageEntity.BOT_COMMAND]).values()), None
# #     )
# #
# #     if not sent_command:
# #         return
# #
# #     if "@" in sent_command:
# #         sent_command = sent_command[: sent_command.index("@")]
# #     sent_command = sent_command[1:]
# #
# #     if sent_command not in command_doc_list:
# #         return
# #
# #     await management.increment(update, context)
# #     logger.info(
# #         "/{} used by user_id:{}".format(sent_command, update.message.from_user.id)
# #     )
# #
# #     await update.message.reply_chat_action(ChatAction.TYPING)
# #     cursor = sqlite_conn.cursor()
# #     cursor.execute(
# #         """
# #         INSERT INTO command_stats (command, user_id) VALUES (?, ?);
# #         """,
# #         (sent_command, update.message.from_user.id),
# #     )
# #
# #
# # async def mention_parser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# #     """
# #     Parse mentions in messages.
# #     """
# #     if not update.message:
# #         return
# #
# #     mentions = update.message.parse_entities(
# #         [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
# #     )
# #
# #     if mentions:
# #         # Regex search text for @<username> mentions
# #         text = update.message.text
# #         usernames = set(re.findall("(@[\w|\d|_]{5,})", text))
# #         await save_mentions(
# #             update.message.from_user.id, [x for x in usernames], update.message
# #         )
# #     elif update.message.reply_to_message:
# #         await save_mentions(
# #             update.message.from_user.id,
# #             [update.message.reply_to_message.from_user.id],
# #             update.message,
# #         )
# #
# #     await management.increment(update, context)