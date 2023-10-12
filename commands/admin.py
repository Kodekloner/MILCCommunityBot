# encoding: utf-8
import os
import re
import datetime
import time
from logging import getLogger
from dotenv import load_dotenv
from dotenv import set_key

from config.db import sqlite_conn

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from wallet.wallet import mnemonic_to_creds, BSC
from wallet.dis_token import distribute_token_winners
from mnemonic import Mnemonic

from constants import BACK
from constants.keys import BACK_KEY
from constants.keys import BACK_TO_HOME_KEY
from constants.messages import SEND_YOUR_MESSAGE
from constants.messages import USER_COUNT
from constants.messages import WELCOME_TO_ADMIN
from constants.messages import WELCOME_TO_HOME
from constants.messages import YOUR_MESSAGE_WAS_SENT
from constants.messages import WELCOME_TO_THE_TWITTER_SECTION
from constants.messages import SET_POINT_SYSTEM
from constants.messages import SET_PRIZE_SYSTEM
from constants.messages import SET_POINT_SYSTEM_WITH_POINTS
from constants.messages import MESSAGE_FOR_SET_POINT
from constants.messages import MESSAGE_FOR_CHANGE_POINT
from constants.messages import MESSAGE_FOR_CHANGE_PRIZE
from constants.messages import MESSAGE_FOR_WRONG_SET_POINT
from constants.messages import MESSAGE_FOR_WRONG_SET_PRIZE
from constants.messages import MESSAGE_FOR_WRONG_CHANGE_PRIZE
from constants.messages import MESSAGE_FOR_SET_PRIZE
from constants.messages import FILE_IS_NOT_VALID
from constants.states import ADD_ADMIN_STATE
from constants.states import ADMIN_STATE
from constants.states import HOME_STATE
from constants.states import TWITTER_STATE
from constants.states import SEARCH_STATE
from constants.states import GET_SEND_TWEETS_STATE
from constants.states import STOP_GET_SEND_TWEETS_STATE
from constants.states import SELECT_STOP_GROUPS_STATE
from constants.states import STOP_SEND_TWEETS_STATE
from constants.states import SELECT_GROUPS_STATE
from constants.states import SEND_TWEETS_STATE
from constants.states import UPLOAD_PHOTO_STATE
from constants.states import SEARCH_DATE_STATE
from constants.states import COMPETITION_STATE
from constants.states import SETUP_POINTS_STATE
from constants.states import INSERT_POINT_STATE
from constants.states import UPDATE_POINT_STATE
from constants.states import LEADERBOARD_SETTING_STATE
from constants.states import SELECT_GROUPS_COMPETITION_STATE
from constants.states import DISPLAY_LEADERBOARD_STATE
from constants.states import SELECT_HIDE_GROUPS_COMPETITION_STATE
from constants.states import HIDE_LEADERBOARD_STATE
from constants.states import TIME_INTERVAL_STATE
from constants.states import STORE_DISPLAY_BOARD_STATE
from constants.states import SETUP_PRIZE_STATE
from constants.states import INSERT_PRIZE_STATE
from constants.states import UPDATE_PRIZE_STATE
from constants.states import SELECT_GROUPS_DIS_STATE
from constants.states import SEND_TOKEN_STATE
from constants.states import PARTICIPANT_STATE
# from constants.states import VIEW_PARTICIPANT_STATE
from constants.states import BAN_PARTICIPANT_STATE
from constants.states import COMFIRM_BAN_PARTICIPANT_STATE
from constants.states import ADMIN_WALLET_STATE
from constants.states import DELETE_WALLET_STATE
# from constants.states import SEND_MESSAGE_TO_ALL_USER
from core.keyboards import admin_keyboard
from core.keyboards import twitter_keyboard
from core.keyboards import get_send_tweets_keyboard
from core.keyboards import stop_get_send_tweets_keyboard
from core.keyboards import select_group_keyboard
from core.keyboards import send_tweets_keyboard
from core.keyboards import stop_send_tweets_keyboard
from core.keyboards import competition_keyboard
from core.keyboards import setup_points_keyboard
from core.keyboards import leaderboard_setting_keyboard
from core.keyboards import display_leaderboard_keyboard
from core.keyboards import hide_leaderboard_keyboard
from core.keyboards import leaderboard_time_settings_keyboard
from core.keyboards import setup_prize_keyboard
from core.keyboards import participant_keyboard
from core.keyboards import yes_or_no_without_back_key
from core.keyboards import back_keyboard
from core.keyboards import back_to_home_keyboard
from core.keyboards import base_keyboard
from core.keyboards import admin_wallet_keyboard
from core.keyboards import dis_token_keyboard
from utils.decorators import restricted, send_action

from commands.twitter import send_tweets, get_tweets, leaderboard, display_board

# Load environment variables from .env file
load_dotenv()

# Init logger
logger = getLogger(__name__)

MEDIA_MIME = None
USER_UPLOADED_FILE_TYPE = None
FILE_PATH_ON_SERVER = None


async def handle_invalid_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle invalid messages."""
    message = update.message
    chat = update.effective_chat

    #Check if message is a command orspecifically mentions the bot's username
    if message.text.startswith("/") or context.bot.username.lower() in message.text.lower() or message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        reply_text = "I'm sorry, but I didn't understand that command or message."
        reply_text += "\n\nHere are some suggestions:"
        reply_text += "\n- Please make sure you're using the correct command."
        reply_text += "\n- Use the keys on the keyboard to send me message."

        await message.reply_text(reply_text)
    elif chat.type == "private":
        reply_text = "I'm sorry, but I didn't understand that command or message."
        reply_text += "\n\nHere are some suggestions:"
        reply_text += "\n- Please make sure you're using the correct command."
        reply_text += "\n- Use the keys on the keyboard to send me message."

        await message.reply_text(reply_text)
    else:
        return


# Function to update the values in the SQL table
def update_table(point_name, value):
    cursor = sqlite_conn.cursor()
    cursor.execute(f"UPDATE point_system SET {point_name} = {value}")

# Function to parse the label and number from a string
def parse_label_and_number(label_number_string):
    label, number = label_number_string.split('-')
    return int(number)

# Function to extract label and number from the input string
def parse_input_string(label_number_string):
    label, number = label_number_string.split('-')
    return label.strip(), int(number)

def process_input(input_string):
    points = input_string.split('\n')
    for point in points:
        if point:
            try:
                point_name, value = parse_input_string(point)
                if point_name not in ['tweets', 'replies', 'likes', 'retweets', 'quotes']:
                    return False  # Invalid point name, return False
                if not isinstance(value, int):
                    return False  # Invalid value, return False
                update_table(point_name, value)
            except ValueError:
                return False
    sqlite_conn.commit()
    return True  # All points are valid, return True

# Function to check if the input string has the correct format and labels
def is_valid_input_string(input_string):
    required_labels = ['tweets', 'replies', 'likes', 'retweets', 'quotes']
    expected_format = "tweets-{number}\nreplies-{number}\nlikes-{number}\nretweets-{number}\nquotes-{number}"
    pattern = expected_format.replace("{number}", r"\d+")
    match = re.match(pattern, input_string)
    if match:
        labels = [label.split('-')[0].strip() for label in input_string.strip().split('\n')]
        return labels == required_labels
    else:
        return False

def check_valid_number(message):
    pattern = r'^\d+(\.\d+)?$'  # Regular expression pattern for float or integer
    if re.match(pattern, message):
        return True  # Valid float or integer
    else:
        return False  # Invalid message

# Function to create the SQL table and insert values
def create_and_insert_table(tweets, replies, likes, retweets, quotes):
    cursor = sqlite_conn.cursor()

    # Insert the values into the table
    cursor.execute('''INSERT INTO point_system (tweets, replies, likes, retweets, quotes)
                      VALUES (?, ?, ?, ?, ?)''', (tweets, replies, likes, retweets, quotes))

    sqlite_conn.commit()  # Commit the changes

def are_user_ids_integers(user_ids):
    if isinstance(user_ids, int):
        # Single user ID
        return True
    else:
        # Invalid input type
        return False

@restricted
@send_action(ChatAction.TYPING)
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        WELCOME_TO_ADMIN,
        reply_markup=admin_keyboard,
        parse_mode=ParseMode.HTML,
    )
    return ADMIN_STATE
    # return ConversationHandler.END

@restricted
@send_action(ChatAction.TYPING)
async def get_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
    rows = cursor.fetchall()

    if rows:
        message = ""

        for index, row in enumerate(rows, start=1):
            title = row["title"]
            print(title)
            entry = f"{index}. <b>{title}</b>\n"
            message += entry

        # Add emojis and formatting
        message = "<b>Groups that use the Bot</b>\n\n" + message
    else:
        message = "<b>Groups that use the Bot</b>\n\nNone"

    await update.message.reply_text(
        text=message,
        reply_markup=base_keyboard,
        parse_mode=ParseMode.HTML,
    )
    return HOME_STATE

@restricted
@send_action(ChatAction.TYPING)
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()

    job_queue = context.job_queue

    for job in job_queue.jobs():
            job.schedule_removal()

    tables = ["tweets", "leaderboard", "TwitterSearch", "leaderboard_time_intervals", "point_system", "prize"]

    for table in tables:
        drop_query = f"DROP TABLE {table};"
        cursor.execute(drop_query)

        if table == "tweets":
            # Table for Tweets
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `tweets` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `tweets` TEXT NOT NULL,
                    `tw_id` INTEGER,
                    `images` TEXT,
                    `created_at` TEXT,
                    `username` TEXT,
                    `sent_at` TEXT,
                    `sent` BOOLEAN
                );
                """
            )

        if table == "leaderboard":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `leaderboard` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `username` TEXT,
                    `tweets` INTEGER,
                    `replies` INTEGER,
                    `likes` INTEGER,
                    `retweets` INTEGER,
                    `quotes` INTEGER,
                    `total` INTEGER
                );
                """
            )

        if table == "TwitterSearch":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `TwitterSearch`(
                    `id` INTEGER PRIMARY KEY,
                    `word` TEXT,
                    `since_id` INTEGER
                );
                """
            )

        if table == "leaderboard_time_intervals":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `leaderboard_time_intervals` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `time_intervals` TEXT
                );
                """
            )

        if table == "point_system":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `point_system` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `tweets` INTEGER,
                    `replies` INTEGER,
                    `likes` INTEGER,
                    `retweets` INTEGER,
                    `quotes` INTEGER
                );
                """
            )

        if table == "prize":
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `prize` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `token` FLOAT(8)
                );
                """
            )




    message = "<b>Bot has been reseted</b>"

    await update.message.reply_text(
        text=message,
        reply_markup=base_keyboard,
        parse_mode=ParseMode.HTML,
    )
    return HOME_STATE

@restricted
@send_action(ChatAction.TYPING)
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Add an admin,\nthey will have access to the admin features\n"
        "Send the userId of the user you want to add.\n"
        "Please it should be correct.\n\n"
        "Example:\n"
        "5311490301",
        reply_markup=back_to_home_keyboard,
    )
    return ADD_ADMIN_STATE

@restricted
@send_action(ChatAction.TYPING)
async def add_admin_to_env(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    admin_id = update.message.text
    if admin_id == BACK_TO_HOME_KEY:
        await update.message.reply_text(
            WELCOME_TO_HOME,
            reply_markup=base_keyboard,
        )
        return HOME_STATE
    else:
        try:
            admin_id = int(admin_id.strip())  # Extract and convert the interval value to an integer
        except ValueError:
            print(admin_id)
            await update.message.reply_text(
                "Please the userId is invalid",
                reply_markup=back_to_home_keyboard,
            )
            return ADD_ADMIN_STATE
        admins = os.environ.get("ADMINS", os.getenv("ADMINS")).split(" ")
        admins.append(str(admin_id))
        admins = list(set(admins))  # Remove duplicates
        admin_string = " ".join(admins)
        os.environ["ADMINS"] = admin_string
        set_key(".env", "ADMINS", admin_string)
        await update.message.reply_text(
            "Admin has been successfully added",
            reply_markup=back_to_home_keyboard,
        )
        return ADD_ADMIN_STATE


@restricted
@send_action(ChatAction.TYPING)
async def twitter(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> str:
    """get user count"""
    # pylint: disable=unused-argument
    # user_count = get_user_count()
    await update.message.reply_text(
        WELCOME_TO_THE_TWITTER_SECTION,
        reply_markup=twitter_keyboard,
    )
    return TWITTER_STATE

@restricted
@send_action(ChatAction.TYPING)
async def back_to_admin(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        WELCOME_TO_ADMIN,
        reply_markup=admin_keyboard,
        parse_mode=ParseMode.HTML,
    )
    return ADMIN_STATE

@restricted
@send_action(ChatAction.TYPING)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM TwitterSearch")
    result = cursor.fetchone()
    if result:
        await update.message.reply_text(
            "These keywords are already searched\n\n"
            f"<b><em>{result['word']}</em></b>\n\n"
            "Change the keywords you want to search for on Twitter.\n\n Example:\n MLT OR #MILC OR @MILCplatform\n\nMLT #MILC @MILCplatform",
            reply_markup=back_keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            "Set the keywords you want to search for on Twitter.\n\n Example:\n MLT OR #MILC OR @MILCplatform\n\nMLT #MILC @MILCplatform",
            reply_markup=back_keyboard,
        )
    return SEARCH_STATE

@restricted
@send_action(ChatAction.TYPING)
async def store_search(update: Update, context: ContextTypes.DEFAULT_TYPE)-> str:
    message = update.message.text
    if message == BACK_KEY:
        await update.message.reply_text(
            WELCOME_TO_THE_TWITTER_SECTION,
            reply_markup=twitter_keyboard
        )
        return TWITTER_STATE

    # Check if any rows exist in the table
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM TwitterSearch")
    result = cursor.fetchone()[0]

    # If rows exist, update the row
    if result > 0:
        cursor.execute("UPDATE TwitterSearch SET word = ? WHERE id = ?", (message, 1))
        await update.message.reply_text(
            "Search word updated successfully, Tap on Send 💬",
            reply_markup=twitter_keyboard,
        )
    else:
        cursor.execute("INSERT INTO TwitterSearch (word) VALUES (?)", (message,))
        await update.message.reply_text(
            "Search Subject added successfully, Tap on Send 💬",
            reply_markup=twitter_keyboard,
        )

    # Commit the changes
    sqlite_conn.commit()

    return TWITTER_STATE

@restricted
@send_action(ChatAction.TYPING)
async def upload_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if FILE_PATH_ON_SERVER is None:
        await update.message.reply_text(
            "Upload an image or GIF that will be used for the tweets",
            reply_markup=back_keyboard,
        )
    else:
        if USER_UPLOADED_FILE_TYPE == "Photo":
            message = "These image is currently used for the tweets\nUpload a new photo or GIF to change it."
            await update.effective_user.send_photo(photo=FILE_PATH_ON_SERVER, caption=message, reply_markup=back_keyboard,)
        elif USER_UPLOADED_FILE_TYPE == "Gif":
            message = "These GIF is currently used for the tweets\nUpload a new photo or GIF to change it."
            await update.effective_user.send_animation(animation=FILE_PATH_ON_SERVER, caption=message, reply_markup=back_keyboard,)
    return UPLOAD_PHOTO_STATE


@restricted
@send_action(ChatAction.TYPING)
async def store_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    global USER_UPLOADED_FILE_TYPE
    global FILE_PATH_ON_SERVER
    global MEDIA_MIME
    message = update.message

    if message.text == "Back ◀️":
        await update.message.reply_text(
            WELCOME_TO_THE_TWITTER_SECTION,
            reply_markup=twitter_keyboard,
        )
        return TWITTER_STATE
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        media = await context.bot.get_file(file_id)
        USER_UPLOADED_FILE_TYPE = "Photo"
    elif update.message.animation:
        file_id = update.message.animation.file_id
        media = await context.bot.get_file(file_id)
        USER_UPLOADED_FILE_TYPE = "Gif"
    else:
        await update.message.reply_text(
            FILE_IS_NOT_VALID,
            reply_markup=back_keyboard,
        )
        return UPLOAD_PHOTO_STATE

    if FILE_PATH_ON_SERVER is not None:
        os.remove(FILE_PATH_ON_SERVER)
        logger.info("media deleted")

        logger.info("starting download media ...")
        file_path = await media.download_to_drive()
        logger.info("download completed")
        FILE_PATH_ON_SERVER = str(file_path)

        if USER_UPLOADED_FILE_TYPE == "Photo":
            message = "Successfully changed the image"
            await update.effective_user.send_photo(photo=FILE_PATH_ON_SERVER, caption=message, reply_markup=back_keyboard,)
        elif USER_UPLOADED_FILE_TYPE == "Gif":
            message = "Successfully changed the GIF"
            await update.effective_user.send_animation(animation=FILE_PATH_ON_SERVER, caption=message, reply_markup=back_keyboard,)
    else:
        logger.info("starting download media ...")
        file_path = await media.download_to_drive()
        logger.info("download completed")
        FILE_PATH_ON_SERVER = str(file_path)

        if USER_UPLOADED_FILE_TYPE == "Photo":
            message = "Successfully uploaded the image"
            await update.effective_user.send_photo(photo=FILE_PATH_ON_SERVER, caption=message, reply_markup=back_keyboard,)
        elif USER_UPLOADED_FILE_TYPE == "Gif":
            message = "Successfully uploaded the GIF"
            await update.effective_user.send_animation(animation=FILE_PATH_ON_SERVER, caption=message, reply_markup=back_keyboard,)
    return UPLOAD_PHOTO_STATE

@restricted
@send_action(ChatAction.TYPING)
async def competition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Control the competition from here",
        reply_markup=competition_keyboard,
    )
    return COMPETITION_STATE

@restricted
@send_action(ChatAction.TYPING)
async def setup_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM point_system")
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(
            SET_POINT_SYSTEM_WITH_POINTS.format(
                                            tweet=result['tweets'],
                                            reply=result['replies'],
                                            like=result['likes'],
                                            retweet=result['retweets'],
                                            quote=result['quotes']
                                        ),
            reply_markup=setup_points_keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await update.message.reply_text(
            SET_POINT_SYSTEM,
            reply_markup=setup_points_keyboard,
        )
    return SETUP_POINTS_STATE


@restricted
@send_action(ChatAction.TYPING)
async def set_point(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM point_system")
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(
            "You have already set the points. To change the points, tap the Change Points button 📝.",
            reply_markup=setup_points_keyboard,
        )
        return SETUP_POINTS_STATE
    else:
        await update.message.reply_text(
            MESSAGE_FOR_SET_POINT,
            reply_markup=back_keyboard,
        )
        return INSERT_POINT_STATE


@restricted
@send_action(ChatAction.TYPING)
async def change_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM point_system")
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(
            MESSAGE_FOR_CHANGE_POINT,
            reply_markup=back_keyboard,
        )
        return UPDATE_POINT_STATE
    else:
        await update.message.reply_text(
            "You have not set the points,\n tap on the Set points button to set the points",
            reply_markup=setup_points_keyboard,
        )
        return SETUP_POINTS_STATE

@restricted
@send_action(ChatAction.TYPING)
async def back_to_competition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Control the competition from here",
        reply_markup=competition_keyboard,
    )
    return COMPETITION_STATE

@restricted
@send_action(ChatAction.TYPING)
async def insertpoint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    points = update.message.text
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM point_system")
    result = cursor.fetchone()

    if points == "Back ◀️":
        if result:
            await update.message.reply_text(
                SET_POINT_SYSTEM_WITH_POINTS.format(
                                                tweet=result['tweets'],
                                                reply=result['replies'],
                                                like=result['likes'],
                                                retweet=result['retweets'],
                                                quote=result['quotes']
                                            ),
                reply_markup=setup_points_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.message.reply_text(
                SET_POINT_SYSTEM,
                reply_markup=setup_points_keyboard,
            )
        return SETUP_POINTS_STATE

    else:
        if result:
            await update.message.reply_text(
                MESSAGE_FOR_WRONG_SET_POINT,
                reply_markup=setup_points_keyboard,
            )
            return SETUP_POINTS_STATE
        else:
            # Check if the input string is valid
            if is_valid_input_string(points):
                # Extract values from the input string
                tweets, replies, likes, retweets, quotes = map(parse_label_and_number, points.split())

                # Store the values in the SQL table
                create_and_insert_table(tweets, replies, likes, retweets, quotes)

                cursor.execute("SELECT * FROM point_system")
                result = cursor.fetchone()
                if result:
                    await update.message.reply_text(
                        SET_POINT_SYSTEM_WITH_POINTS.format(
                                                    tweet=result['tweets'],
                                                    reply=result['replies'],
                                                    like=result['likes'],
                                                    retweet=result['retweets'],
                                                    quote=result['quotes']
                                                ),
                        reply_markup=setup_points_keyboard,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    return SETUP_POINTS_STATE
            else:
                await update.message.reply_text(
                    "Invalid input please follow the format",
                    reply_markup=back_keyboard,
                )
                return INSERT_POINT_STATE

@restricted
@send_action(ChatAction.TYPING)
async def updatepoint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    points = update.message.text
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM point_system")
    result = cursor.fetchone()

    if points == "Back ◀️":
        if result:
            await update.message.reply_text(
                SET_POINT_SYSTEM_WITH_POINTS.format(
                                                tweet=result['tweets'],
                                                reply=result['replies'],
                                                like=result['likes'],
                                                retweet=result['retweets'],
                                                quote=result['quotes']
                                            ),
                reply_markup=setup_points_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.message.reply_text(
                SET_POINT_SYSTEM,
                reply_markup=setup_points_keyboard,
            )
        return SETUP_POINTS_STATE

    else:
        if result:
            # Check if the input string is valid
            if process_input(points):
                cursor.execute("SELECT * FROM point_system")
                result = cursor.fetchone()
                if result:
                    await update.message.reply_text(
                        SET_POINT_SYSTEM_WITH_POINTS.format(
                                                    tweet=result['tweets'],
                                                    reply=result['replies'],
                                                    like=result['likes'],
                                                    retweet=result['retweets'],
                                                    quote=result['quotes']
                                                ),
                        reply_markup=setup_points_keyboard,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    return SETUP_POINTS_STATE
            else:
                await update.message.reply_text(
                    "Invalid input please follow the format",
                    reply_markup=back_keyboard,
                )
                return UPDATE_POINT_STATE
        else:
            await update.message.reply_text(
                MESSAGE_FOR_WRONG_SET_POINT,
                reply_markup=setup_points_keyboard,
            )
            return SETUP_POINTS_STATE

@restricted
@send_action(ChatAction.TYPING)
async def star_comp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    from datetime import datetime, timedelta, time

    chat_id = update.effective_message.chat_id
    # Get the current timestamp

    job_params = False
    # Format the previous day as "YYYY-MM-DD"
    # formatted_time = previous_day.strftime("%Y-%m-%d")

    job_queue = context.job_queue

    if any(job.callback == leaderboard for job in job_queue.jobs()):
        await update.message.reply_text(
            "Bot has already started the competition",
            reply_markup=competition_keyboard,
        )
        return COMPETITION_STATE

    cursor = sqlite_conn.cursor()
    drop_query = f"DROP TABLE leaderboard;"
    cursor.execute(drop_query)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `leaderboard` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `username` TEXT,
            `tweets` INTEGER,
            `replies` INTEGER,
            `likes` INTEGER,
            `retweets` INTEGER,
            `quotes` INTEGER,
            `total` INTEGER
        );
        """
    )

    sqlite_conn.commit()

    # context.job_queue.run_repeating(leaderboard, interval=600, first=1, chat_id=chat_id, name=str(chat_id), data=job_params)
    context.job_queue.run_daily(leaderboard, time=time(22, 30), chat_id=chat_id, name=str(chat_id), data=job_params)

    await update.message.reply_text(
        "Processing ...\n\nYou will recieve a message in the night at about 11:00pm if it was successful or not.",
        reply_markup=competition_keyboard,
    )
    return COMPETITION_STATE

@restricted
@send_action(ChatAction.TYPING)
async def stop_comp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    job_queue = context.job_queue

    if any(job.callback == leaderboard for job in job_queue.jobs()):
        for job in job_queue.jobs():
            if job.callback == leaderboard:
                job.schedule_removal()

        await update.message.reply_text(
            "Competition successfully stopped.",
            reply_markup=competition_keyboard,
        )
        return COMPETITION_STATE
    else:
        await update.message.reply_text(
            "The competition have not started yet. Start the competition",
            reply_markup=competition_keyboard,
        )
        return COMPETITION_STATE

@restricted
@send_action(ChatAction.TYPING)
async def comp_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please follow the procedure:\nFirst, set the time interval for the leaderboard. Then tap on display.\nIf you want to stop, tap Hide.",
        reply_markup=leaderboard_setting_keyboard,
    )
    return LEADERBOARD_SETTING_STATE

@restricted
@send_action(ChatAction.TYPING)
async def leaderboard_time_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM leaderboard_time_intervals")
    result = cursor.fetchone()

    if result:
        time_interval = result['time_intervals']
        interval_parts = time_interval.split("-")
        time = interval_parts[0].strip()
        value = interval_parts[1].strip()
        await update.message.reply_text(
            f"The time interval is currently set to:\nEvery {value} {time}\n\nUse the following buttons to update the time interval👇",
            reply_markup=leaderboard_time_settings_keyboard,
        )
    else:
        await update.message.reply_text(
            f"Time Interval is not set\n\nUse the keys below to set the time interval👇",
            reply_markup=leaderboard_time_settings_keyboard,
        )
    return TIME_INTERVAL_STATE

@restricted
@send_action(ChatAction.TYPING)
async def set_time_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    time_interval = update.message.text
    if time_interval == "Back ◀️":
        await update.message.reply_text(
            "Please follow the procedure:\nFirst, set the time interval for the leaderboard. Then tap on display.\nIf you want to stop, tap Hide.",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

    elif time_interval in ("Sec(s)", "Min(s)", "Hour(s)", "Day(s)"):
        time_interval = time_interval.lower()
        context.user_data['time_interval'] = time_interval  # Store the interval unit in the user data
        await update.message.reply_text(
            "Enter the interval value (integer):",
            reply_markup=back_keyboard,
        )
        return STORE_DISPLAY_BOARD_STATE

    else:
        await update.message.reply_text(
            'Invalid Command',
            reply_markup=leaderboard_time_settings_keyboard,
        )
        return TIME_INTERVAL_STATE


@restricted
@send_action(ChatAction.TYPING)
async def store_time_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM leaderboard_time_intervals")
    result = cursor.fetchone()
    time_interval_value = update.message.text
    if time_interval_value == "Back ◀️":
        if result:
            time_interval = result['time_intervals']
            interval_parts = time_interval.split("-")
            time = interval_parts[0].strip()
            value = interval_parts[1].strip()
            await update.message.reply_text(
                f"The time interval is currently set to:\nEvery {value} {time}\nUse the following buttons to update the time interval👇\n",
                reply_markup=leaderboard_time_settings_keyboard,
            )
        else:
            await update.message.reply_text(
                f"Time Interval is not set\n\nUse the Keys below to update the time interval👇",
                reply_markup=leaderboard_time_settings_keyboard,
            )
        return TIME_INTERVAL_STATE

    else:
        try:
            time_interval_value = int(time_interval_value.strip())  # Extract and convert the interval value to an integer
        except ValueError:
            await update.message.reply_text(
                "Please an valid number\nExample: \n1",
                reply_markup=back_keyboard,
            )
            return STORE_DISPLAY_BOARD_STATE

        time_interval = context.user_data.get('time_interval')  # Retrieve the interval unit from the user data

        if time_interval:
            interval_message = f"{time_interval}-{time_interval_value}"

            if result:
                # Update the time interval in the database
                cursor.execute("UPDATE leaderboard_time_intervals SET time_intervals = ?", (interval_message,))
                sqlite_conn.commit()
                await update.message.reply_text(
                    f"Time Interval has be successfully updated to:\nEvery {time_interval_value} {time_interval}\n\nGo back to display the leaerboard using the set time interval",
                    reply_markup=leaderboard_time_settings_keyboard,
                )
            else:
                cursor.execute('INSERT INTO leaderboard_time_intervals (time_intervals) VALUES (?)',
                               (interval_message,))
                sqlite_conn.commit()
                await update.message.reply_text(
                    f"Time Interval has be successfully Set to:\nEvery {time_interval_value} {time_interval}\n\nGo back to display the leaerboard using the set time interval",
                    reply_markup=leaderboard_time_settings_keyboard,
                )

        else:
            await update.message.reply_text(
                f"There was an issue",
                reply_markup=leaderboard_time_settings_keyboard,
            )
        return TIME_INTERVAL_STATE


@restricted
@send_action(ChatAction.TYPING)
async def get_groups_display_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text(
            "No group has been recognised yet.",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

    # Create a list to store the inline keyboard buttons
    keyboard = []

    # Iterate through the titles and create a button for each
    for row in rows:
        group_name = row['title']
        if not any(job.name == group_name and job.callback == display_board for job in job_queue.jobs()):
            button = InlineKeyboardButton(group_name, callback_data=group_name)
            keyboard.append([button])


    if keyboard == []:
        await update.message.reply_text(
            "Bot is already displaying leaderboard to all group(s).",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

    # Create the inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the inline keyboard to the user
    await update.message.reply_text('Select the group(s) to display Leaderboard:', reply_markup=reply_markup)
    await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

    return SELECT_GROUPS_COMPETITION_STATE


# Callback query handler
async def button_callback_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_com_title = query.data
    user_data = context.user_data.setdefault('selected_com_titles', [])

    if selected_com_title in user_data:
        user_data.remove(selected_com_title)
    else:
        user_data.append(selected_com_title)

    await query.answer()

    return SELECT_GROUPS_COMPETITION_STATE


# Callback query handler
async def get_selected_groups_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proceed = update.message.text
    if proceed == BACK_KEY:
        user_data = context.user_data.get('selected_com_titles')
        if user_data:
            # Clear the user_data
            context.user_data['selected_com_titles'] = []

        await update.message.reply_text(
            "Please follow the procedure:\nFirst, set the time interval for the leaderboard. Then tap on display.\nIf you want to stop, tap Hide.",
             reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

    elif proceed == "Proceed":
        user_data = context.user_data.get('selected_com_titles')
        if user_data:
            message = "Are you sure you want to display Leaderboard to these group(s):\n\n"

            for index, data in enumerate(user_data, start=1):
                entry = f"{index}. <b>{data}</b>\n"
                message += entry
            await update.message.reply_text(message, reply_markup=display_leaderboard_keyboard, parse_mode=ParseMode.HTML)
            return DISPLAY_LEADERBOARD_STATE
        else:
            await update.message.reply_text("You haven't selected any group(s).")
    else:
        await update.message.reply_text("Invalid message.")
    return SELECT_GROUPS_COMPETITION_STATE


@restricted
@send_action(ChatAction.TYPING)
async def display_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    display = update.message.text
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue
    user_data = context.user_data.get('selected_com_titles')
    cursor = sqlite_conn.cursor()

    if display == BACK_KEY:
        if user_data:
            context.user_data['selected_com_titles'] = []

        cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "No group has been recognised yet.",
                reply_markup=leaderboard_setting_keyboard,
            )
            return LEADERBOARD_SETTING_STATE

        # Create a list to store the inline keyboard buttons
        keyboard = []

        # Iterate through the titles and create a button for each
        for row in rows:
            group_name = row['title']
            if not any(job.name == group_name and job.callback == display_board for job in job_queue.jobs()):
                button = InlineKeyboardButton(group_name, callback_data=group_name)
                keyboard.append([button])


        if keyboard == []:
            await update.message.reply_text(
                "Bot is already displaying leaderboard to all group(s).",
                reply_markup=leaderboard_setting_keyboard,
            )
            return LEADERBOARD_SETTING_STATE

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the inline keyboard to the user
        await update.message.reply_text('Select the group(s) to display leaderboard:', reply_markup=reply_markup)
        await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

        return SELECT_GROUPS_COMPETITION_STATE

    elif display == "Display":
        cursor.execute("SELECT * FROM leaderboard_time_intervals")
        result = cursor.fetchone()
        if result:
            time_interval_message = result["time_intervals"]

            # Split the interval string into unit and value
            interval_parts = time_interval_message.split("-")

            # Extract the unit and value
            interval_unit = interval_parts[0].strip()
            interval_value = int(interval_parts[1].strip())

            # Remove the parentheses from the unit
            interval_unit = interval_unit.replace("(", "").replace(")", "")

            # Define conversion factors for each unit
            conversion_factors = {
                "secs": 1,
                "mins": 60,
                "hours": 3600,
                "days": 86400
            }

            # Convert the interval to seconds
            if interval_unit in conversion_factors:
                seconds = interval_value * conversion_factors[interval_unit]

            for index, data in enumerate(user_data):
                groups = [False, False]
                groups.append(data)
                context.job_queue.run_repeating(display_board, interval=seconds, first=1, chat_id=chat_id, name=str(data), data=groups)

            await update.message.reply_text(
                "Processing ...",
                reply_markup=leaderboard_setting_keyboard,
            )
        else:
            await update.message.reply_text(
                "Please Set the time interval first before displaying the leaderboard",
                reply_markup=leaderboard_setting_keyboard,
            )
        return LEADERBOARD_SETTING_STATE

@restricted
@send_action(ChatAction.TYPING)
async def get_groups_hide_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue
    cursor = sqlite_conn.cursor()

    cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
    rows = cursor.fetchall()

    if not rows:
        await update.message.reply_text(
            "No group have been recognised yet.",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

    # Create a list to store the inline keyboard buttons
    keyboard = []

    # Iterate through the titles and create a button for each
    for row in rows:
        group_name = row['title']
        if any(job.name == group_name and job.callback == display_board for job in job_queue.jobs()):
            button = InlineKeyboardButton(group_name, callback_data=group_name)
            keyboard.append([button])

    if keyboard == []:
        await update.message.reply_text(
            "The competition leaderboard is not displayed in any group(s).\nSet a time interval if you do not have one yet.\nDisplay and hide the leaderboard whenever you want.",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

    # Create the inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the inline keyboard to the user
    await update.message.reply_text('Select the group(s) to hide the leaderboard for:', reply_markup=reply_markup)
    await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

    return SELECT_HIDE_GROUPS_COMPETITION_STATE


# Callback query handler
async def button_callback_hide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_hide_title = query.data
    user_data = context.user_data.setdefault('selected_hide_titles', [])

    if selected_hide_title in user_data:
        user_data.remove(selected_hide_title)
    else:
        user_data.append(selected_hide_title)

    await query.answer()

    return SELECT_HIDE_GROUPS_COMPETITION_STATE


# Callback query handler
async def get_selected_hide_groups_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proceed = update.message.text
    user_data = context.user_data.get('selected_hide_titles')

    if proceed == BACK_KEY:
        user_data = context.user_data.get('selected_hide_titles')
        if user_data:
            # Clear the user_data
            context.user_data['selected_hide_titles'] = []

        await update.message.reply_text(
            "Please follow the procedure:\nFirst, set the time interval for the leaderboard. Then tap on display.\nIf you want to stop, tap Hide.",
             reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

    elif proceed == "Proceed":
        if user_data:
            message = "Are you sure you want to hide the leaderboard of this group(s):\n\n"

            for index, data in enumerate(user_data, start=1):
                entry = f"{index}. <b>{data}</b>\n"
                message += entry

            await update.message.reply_text(message, reply_markup=hide_leaderboard_keyboard, parse_mode=ParseMode.HTML)
            return HIDE_LEADERBOARD_STATE
        else:
            await update.message.reply_text("You haven't selected any group(s).")
    else:
        await update.message.reply_text("Invalid message.")
    return SELECT_HIDE_GROUPS_COMPETITION_STATE


@restricted
@send_action(ChatAction.TYPING)
async def hide_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue
    hide = update.message.text
    user_data = context.user_data.get('selected_hide_titles')

    if hide == BACK_KEY:
        if user_data:
            context.user_data['selected_hide_titles'] = []

        cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "No group have been recognised yet.",
                reply_markup=leaderboard_setting_keyboard,
            )
            return LEADERBOARD_SETTING_STATE

        # Create a list to store the inline keyboard buttons
        keyboard = []

        # Iterate through the titles and create a button for each
        for row in rows:
            group_name = row['title']
            if any(job.name == group_name and job.callback == display_board for job in job_queue.jobs()):
                button = InlineKeyboardButton(group_name, callback_data=group_name)
                keyboard.append([button])

        if keyboard == []:
            await update.message.reply_text(
                "The Competition leaderboard is not been displayed in any group(s)\n\nSet time interval if you have not\n\nDisplay Leaderboard then hide it any time you want to.",
                reply_markup=leaderboard_setting_keyboard,
            )
            return LEADERBOARD_SETTING_STATE

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the inline keyboard to the user
        await update.message.reply_text('Select the group(s) to hide the leaderboard for:', reply_markup=reply_markup)
        await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

        return SELECT_HIDE_GROUPS_COMPETITION_STATE

    elif hide == "Hide":
        for index, data in enumerate(user_data):
            if any(job.name == data and job.callback == display_board for job in job_queue.jobs()):
                for job in job_queue.jobs():
                    if job.name == data and job.callback == display_board:
                        job.schedule_removal()

        await update.message.reply_text(
            "Bot has hide leaderboard for the selected groups.",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE


@restricted
@send_action(ChatAction.TYPING)
async def comp_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        'Manage participant(s)',
        reply_markup=participant_keyboard,
    )
    return PARTICIPANT_STATE

@restricted
@send_action(ChatAction.TYPING)
async def view_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # SELECT user_wallet_twitter.username, user_wallet_twitter.chat_id, leaderboard.id, leaderboard.tweets, leaderboard.replies, leaderboard.likes, leaderboard.retweets, leaderboard.quotes, leaderboard.total
    # FROM leaderboard
    # JOIN user_wallet_twitter ON leaderboard.username = user_wallet_twitter.twitter_username
    # WHERE user_wallet_twitter.ban = ? AND user_wallet_twitter.chat_id = ?
    # ORDER BY leaderboard.total DESC
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE ban=?", (False,),)
    results = cursor.fetchall()
    if results:
        # Prepare the leaderboard message
        message = ""

        for index, result in enumerate(results, start=1):
            username = result["username"]
            entry = f"{index}. {username}\n"
            message += entry

        # Add emojis and formatting
        message = "👨‍💼 <b>Participant(s)</b> 👩‍💼\n\n" + message

        await update.message.reply_text(
            message,
            reply_markup=participant_keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            "You don't have a participant yet",
            reply_markup=participant_keyboard,
        )
    return PARTICIPANT_STATE

@restricted
@send_action(ChatAction.TYPING)
async def ban_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        'Input the username of the participant you want to ban',
        reply_markup=back_keyboard,
    )
    return BAN_PARTICIPANT_STATE

@restricted
@send_action(ChatAction.TYPING)
async def comfirm_ban_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    ban = update.message.text
    context.user_data['user_to_ban'] = ban
    if ban == "Back ◀️":
        await update.message.reply_text(
            'Manage participant(s)',
            reply_markup=participant_keyboard,
        )
        return PARTICIPANT_STATE
    else:
        await update.message.reply_text(
            'Are you sure you want to ban these users',
            reply_markup=yes_or_no_without_back_key,
        )
        return COMFIRM_BAN_PARTICIPANT_STATE


@restricted
@send_action(ChatAction.TYPING)
async def delete_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    ban = update.message.text
    if ban == "Yes":
        user_to_ban = context.user_data.get('user_to_ban')
        cursor = sqlite_conn.cursor()
        cursor.execute("DELETE FROM user_wallet_twitter WHERE username=?", (user_to_ban,),)

        if cursor.rowcount > 0:
            await update.message.reply_text(
                f'{user_to_ban} has been successfully deleted',
                reply_markup=participant_keyboard,
            )
            return PARTICIPANT_STATE
        else:
            await update.message.reply_text(
                f'No user named {user_to_ban}\nOr {user_to_ban} has already been ban',
                reply_markup=participant_keyboard,
            )
        return PARTICIPANT_STATE
    elif ban == "No":
        await update.message.reply_text(
            'Manage participant(s)',
            reply_markup=participant_keyboard,
        )
        return PARTICIPANT_STATE

@restricted
@send_action(ChatAction.TYPING)
async def dis_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Set the prize for each position in the competition; and distribute tokens to the winners.\n",
        reply_markup=setup_prize_keyboard,
    )
    return SETUP_PRIZE_STATE


@restricted
@send_action(ChatAction.TYPING)
async def set_prize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM prize")
    results = cursor.fetchall()

    if results:
        message = "<b>Current prize(s)</b>\n"
        for result in results:
            message += f"{str(result['id'])}-{str(result['token'])}\n"

        message += "\n"
        message += "You have already set the prize. To change the prize, tap the Change Prize button."
        await update.message.reply_text(
            message,
            reply_markup=setup_prize_keyboard,
            parse_mode=ParseMode.HTML,
        )
        return SETUP_PRIZE_STATE
    else:
        await update.message.reply_text(
            MESSAGE_FOR_SET_PRIZE,
            reply_markup=back_keyboard,
        )
        return INSERT_PRIZE_STATE



@restricted
@send_action(ChatAction.TYPING)
async def change_prize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM prize")
    results = cursor.fetchall()

    if results:
        message = "<b>Current prize(s)</b>\n"
        for result in results:
            message += f"{result['id']}-{result['token']}\n"

        message += "\n"
        message += MESSAGE_FOR_CHANGE_PRIZE
        await update.message.reply_text(
            message,
            reply_markup=back_keyboard,
            parse_mode=ParseMode.HTML,
        )
        return UPDATE_PRIZE_STATE
    else:
        await update.message.reply_text(
            "You have not set the prize,\nTap on the Set prize button to set the prizes",
            reply_markup=setup_prize_keyboard,
        )
        return SETUP_PRIZE_STATE

@restricted
@send_action(ChatAction.TYPING)
async def insertprize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    prizes = update.message.text
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM prize")
    results = cursor.fetchall()

    if prizes == "Back ◀️":
        await update.message.reply_text(
            SET_PRIZE_SYSTEM,
            reply_markup=setup_prize_keyboard,
        )
        return SETUP_PRIZE_STATE

    else:
        prizes = prizes.strip().split('\n')

        # Check if the input string is valid
        for prize in prizes:
            if not check_valid_number(prize):
                await update.message.reply_text(
                    "Invalid input please follow the format",
                    reply_markup=back_keyboard,
                )
                return INSERT_PRIZE_STATE

        cursor = sqlite_conn.cursor()
        for prize in prizes:
            cursor.execute("INSERT INTO prize (token) VALUES (?)", (prize,))
            sqlite_conn.commit()

        cursor.execute("SELECT * FROM prize")
        results = cursor.fetchall()
        if results:
            message = ""
            for result in results:
                message += f"{result['id']}-{result['token']}\n"

            message += "\n"
            message += "To change the prize, tap the Change Prize button"
            message = "successfully set competition prize\n\n" + message
            await update.message.reply_text(
                message,
                reply_markup=setup_prize_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
            return SETUP_PRIZE_STATE


@restricted
@send_action(ChatAction.TYPING)
async def updateprize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    prizes = update.message.text
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM prize")
    results = cursor.fetchall()

    if prizes == "Back ◀️":
        message = "<b>Current prize(s)</b>\n"
        for result in results:
            message += f"{result['id']}-{result['token']}\n"

        message += "\n"
        message += "To change the prize, tap the Change Prize button"
        await update.message.reply_text(
            message,
            reply_markup=setup_prize_keyboard,
            parse_mode=ParseMode.HTML,
        )
        return SETUP_PRIZE_STATE

    else:
        prizes = prizes.strip().split('\n')
        for prize in prizes:
            if "-" not in prize:
                await update.message.reply_text(
                    "Invalid input please follow the format",
                    reply_markup=back_keyboard,
                )
                return UPDATE_PRIZE_STATE

            id_number = prize.split("-")
            if len(id_number) != 2:
                await update.message.reply_text(
                    "Invalid input please follow the format",
                    reply_markup=back_keyboard,
                )
                return UPDATE_PRIZE_STATE

            position = id_number[0]
            prize_value = id_number[1]

            if not position.isdigit() or not check_valid_number(prize_value):
                await update.message.reply_text(
                    "Invalid input please follow the format",
                    reply_markup=back_keyboard,
                )
                return UPDATE_PRIZE_STATE

            position = int(position)

            cursor.execute("INSERT OR REPLACE INTO prize (id, token) VALUES (?, ?)", (position, prize_value))
            sqlite_conn.commit()

        cursor.execute("SELECT * FROM prize")
        results = cursor.fetchall()
        message = ""
        for result in results:
            message += f"{result['id']}-{result['token']}\n"

        message += "\n"
        message = "successfully changed competition prize\n\n" + message

        await update.message.reply_text(
            message,
            reply_markup=setup_prize_keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )
        return SETUP_PRIZE_STATE


@restricted
@send_action(ChatAction.TYPING)
async def get_groups_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM prize")
    results = cursor.fetchall()

    if results:
        cursor.execute("SELECT * FROM admin_wallet")
        result = cursor.fetchone()
        if result:
            cursor = sqlite_conn.cursor()
            cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
            rows = cursor.fetchall()

            if not rows:
                await update.message.reply_text(
                    "No group is recongised yet.",
                    reply_markup=setup_prize_keyboard,
                )
                return SETUP_PRIZE_STATE

            # Create a list to store the inline keyboard buttons
            keyboard = []

            for row in rows:
                group_name = row['title']
                button = InlineKeyboardButton(group_name, callback_data=group_name)
                keyboard.append([button])

            # Create the inline keyboard markup
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send the inline keyboard to the user
            await update.message.reply_text('Select the group(s) to send tokens to winners:', reply_markup=reply_markup)
            await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

            return SELECT_GROUPS_DIS_STATE

            # await update.message.reply_text(
            #     f"Insuffient fonds\n\n<b>Balance:</b> {result['balance']} BNB",
            #     reply_markup=setup_prize_keyboard,
            #     parse_mode=ParseMode.HTML,
            # )
            # SELECT_GROUPS_DIS_STATE
        else:
            await update.message.reply_text(
                "You don't have an admin wallet, to control the distribution",
                reply_markup=setup_prize_keyboard,
            )
    else:
        await update.message.reply_text(
            "Set prize for each position in the competition.\nBefore send token",
            reply_markup=setup_prize_keyboard,
        )
    return SETUP_PRIZE_STATE


# Callback query handler
async def button_callback_dis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_dis_title = query.data
    user_data = context.user_data.setdefault('selected_dis_titles', [])

    if selected_dis_title in user_data:
        user_data.remove(selected_dis_title)
    else:
        user_data.append(selected_dis_title)

    await query.answer()

    return SELECT_GROUPS_DIS_STATE


# Callback query handler
async def get_selected_groups_dis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proceed = update.message.text
    if proceed == BACK_KEY:
        user_data = context.user_data.get('selected_dis_titles')
        if user_data:
            # Clear the user_data
            context.user_data['selected_dis_titles'] = []

        await update.message.reply_text(
            "Set the prize for each position in the competition; and distribute tokens to the winners.",
            reply_markup=setup_prize_keyboard,
        )
        return SETUP_PRIZE_STATE

    elif proceed == "Proceed":
        user_data = context.user_data.get('selected_dis_titles')
        if user_data:
            message = "Are you sure you want to distribute tokens to the winners of group(s):\n\n"

            for index, data in enumerate(user_data, start=1):
                entry = f"{index}. <b>{data}</b>\n"
                message += entry
            await update.message.reply_text(message, reply_markup=dis_token_keyboard, parse_mode=ParseMode.HTML)
            return SEND_TOKEN_STATE
        else:
            await update.message.reply_text("You haven't selected any group(s).")
    else:
        await update.message.reply_text("Invalid message.")
    return SELECT_GROUPS_DIS_STATE


@restricted
@send_action(ChatAction.TYPING)
async def send_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    send_token = update.message.text
    if send_token == BACK_KEY:
        user_data = context.user_data.get('selected_dis_titles')
        if user_data:
            # Clear the user_data
            context.user_data['selected_dis_titles'] = []

        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "No group is recongised yet.",
                reply_markup=setup_prize_keyboard,
            )
            return SETUP_PRIZE_STATE

        # Create a list to store the inline keyboard buttons
        keyboard = []

        for row in rows:
            group_name = row['title']
            button = InlineKeyboardButton(group_name, callback_data=group_name)
            keyboard.append([button])

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the inline keyboard to the user
        await update.message.reply_text('Select the group(s) to send tokens to winners:', reply_markup=reply_markup)
        await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

        return SELECT_GROUPS_DIS_STATE

    elif send_token == "Send Token":
        chat_id = update.effective_message.chat_id
        user_data = context.user_data.get('selected_dis_titles')

        await update.message.reply_text(
            "Processing ...",
            reply_markup=setup_prize_keyboard,
        )
        for data in user_data:
            await distribute_token_winners(data, chat_id, context)
        return SETUP_PRIZE_STATE
    else:
        await update.message.reply_text(
            "Invalid Message",
            reply_markup=setup_prize_keyboard,
        )
        return SETUP_PRIZE_STATE

@restricted
@send_action(ChatAction.TYPING)
async def admin_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Get admin wallet",
        reply_markup=admin_wallet_keyboard,
    )
    return ADMIN_WALLET_STATE

@restricted
@send_action(ChatAction.TYPING)
async def create_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM admin_wallet")
    result = cursor.fetchone()

    # Check if the table is empty
    if result[0] == 0:
        rows = cursor.fetchone()

        mnemo = Mnemonic("english")

        words = mnemo.generate(strength=256)

        seed = mnemo.to_seed(words, passphrase="telegram bot wallet")

        entropy = mnemo.to_entropy(words)

        # Get the private key and wallet address using the Seed phrase
        address, private_key = mnemonic_to_creds(words)

        # Construct from private_key and address
        wallet = BSC(private_key, address)

        # Get wallet balance
        balance = wallet.balance()

        cursor.execute('INSERT INTO admin_wallet (address, private_key, mnemonic, balance) VALUES (?, ?, ?, ?)',
                       (address, private_key, words, balance))
        sqlite_conn.commit()

        await update.message.reply_text(
            "Created admin wallet successfully, view the wallet details by clicking the button",
            reply_markup=admin_wallet_keyboard,
        )

    else:
        await update.message.reply_text(
            "Admin wallet already created, view the wallet details by clicking the button",
            reply_markup=admin_wallet_keyboard,
        )

    return ADMIN_WALLET_STATE

@restricted
@send_action(ChatAction.TYPING)
async def view_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM admin_wallet")
    result = cursor.fetchone()

    # Check if the table is empty
    if result[0] == 0:
        await update.message.reply_text(
            "Please create an admin wallet first",
            reply_markup=admin_wallet_keyboard,
        )
    else:
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM admin_wallet")
        result = cursor.fetchone()

        private_key = result['private_key']
        address = result['address']

        # Construct from private_key and address
        wallet = BSC(private_key, address)

        # Get wallet balance
        balance = wallet.balance_of_token()
        balance_of_bnb = wallet.balance()
        balance = str(balance)
        print(balance)

        cursor.execute("UPDATE admin_wallet SET balance = ? WHERE id = ?", (balance, 1))

        # Send the wallet details to the user
        await update.message.reply_text(f"<b>Mnemonic words:</b> {result['mnemonic']}\n\n<b>Wallet address:</b> {result['address']}\n\n<b>Private key:</b> {result['private_key']}\n\n<b>Balance of BNB:</b> {balance_of_bnb} BNB\n\n<b>Balance:</b> {balance} MLT",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_wallet_keyboard,
        )
    return ADMIN_WALLET_STATE

@restricted
@send_action(ChatAction.TYPING)
async def delete_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM admin_wallet")
    result = cursor.fetchone()
    if result:
        await update.message.reply_text(
            'Are you sure you want to delete the admin wallet',
            reply_markup=yes_or_no_without_back_key,
        )
        return DELETE_WALLET_STATE
    else:
        await update.message.reply_text(
            "You have don't have an admin wallet create one",
            reply_markup=admin_wallet_keyboard,
        )
        return ADMIN_WALLET_STATE

@restricted
@send_action(ChatAction.TYPING)
async def comfirm_delete_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    delete = update.message.text
    if delete == "Yes":
        cursor = sqlite_conn.cursor()
        cursor.execute("DELETE FROM admin_wallet")
        sqlite_conn.commit()
        await update.message.reply_text(
            'Deleted successfully',
            reply_markup=admin_wallet_keyboard,
        )
        return ADMIN_WALLET_STATE
    elif delete == "No":
        await update.message.reply_text(
            'Admin wallet',
            reply_markup=admin_wallet_keyboard,
        )
        return ADMIN_WALLET_STATE


@restricted
@send_action(ChatAction.TYPING)
async def add_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Which date would you like to start searching form on twitter. Example '2023-04-28' without the ''.",
        reply_markup=back_keyboard,
    )
    return SEARCH_DATE_STATE

@restricted
@send_action(ChatAction.TYPING)
async def store_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.message.text
    if message == BACK_KEY:
        await update.message.reply_text(
            WELCOME_TO_THE_TWITTER_SECTION,
            reply_markup=twitter_keyboard
        )
        return TWITTER_STATE

    # Check if any rows exist in the table
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM TwitterSearch")
    result = cursor.fetchone()[0]

    # If rows exist, update the row
    if result > 0:
        cursor.execute("UPDATE TwitterSearch SET time = ? WHERE id = ?", (message, 1))
        await update.message.reply_text(
            "Search date updated successfully, Now you can now start send tweets",
            reply_markup=twitter_keyboard,
        )
    else:
        cursor.execute("INSERT INTO TwitterSearch (time) VALUES (?)", (message,))
        await update.message.reply_text(
            "Search date added successfully, Now you can now start sending tweets",
            reply_markup=twitter_keyboard,
        )

    # Commit the changes
    sqlite_conn.commit()
    return TWITTER_STATE


@restricted
@send_action(ChatAction.TYPING)
async def get_send_tweet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        'Please make sure you get the tweets before sending them to the group(s).',
         reply_markup=get_send_tweets_keyboard,
     )
    return GET_SEND_TWEETS_STATE


@restricted
@send_action(ChatAction.TYPING)
async def get_tweets_select_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue
    cursor = sqlite_conn.cursor()
    get_send_tweet = update.message.text

    if get_send_tweet == BACK_KEY:
        await update.message.reply_text(
            WELCOME_TO_THE_TWITTER_SECTION,
            reply_markup=twitter_keyboard,
        )
        return TWITTER_STATE

    elif get_send_tweet ==  "Get tweets":
        if any(job.callback == get_tweets for job in job_queue.jobs()):
            await update.message.reply_text(
                "Bot is already getting Tweets.",
                reply_markup=get_send_tweets_keyboard,
            )
            return GET_SEND_TWEETS_STATE

        cursor.execute("SELECT * FROM tweets")
        results = cursor.fetchall()
        if results:
            cursor.execute("DELETE FROM tweets")
            cursor.execute("UPDATE TwitterSearch SET since_id=? WHERE id=?", (None, 1))
            sqlite_conn.commit()

        sent = False
        # context.job_queue.run_repeating(get_tweets, interval=20, first=1, chat_id=chat_id, name=str(chat_id), data=sent)
        context.job_queue.run_repeating(get_tweets, interval=900, first=1, chat_id=chat_id, name=str(chat_id), data=sent)

        await update.message.reply_text(
            "Processing ...",
            reply_markup=get_send_tweets_keyboard,
        )
        return GET_SEND_TWEETS_STATE

    elif get_send_tweet == "Send 💬":
        chat_id = update.effective_message.chat_id
        job_queue = context.job_queue
        cursor = sqlite_conn.cursor()

        cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "No group have been recognised yet.",
                reply_markup=get_send_tweets_keyboard,
            )
            return GET_SEND_TWEETS_STATE

        # Create a list to store the inline keyboard buttons
        keyboard = []

        # Iterate through the titles and create a button for each
        for row in rows:
            group_name = row['title']
            if not any(job.name == group_name and job.callback == send_tweets for job in job_queue.jobs()):
                button = InlineKeyboardButton(group_name, callback_data=group_name)
                keyboard.append([button])

        if keyboard == []:
            await update.message.reply_text(
                "Bot is already sending tweets to all group(s).",
                reply_markup=get_send_tweets_keyboard,
            )
            return GET_SEND_TWEETS_STATE

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the inline keyboard to the user
        await update.message.reply_text('Select the group(s) to which tweets are to be sent:', reply_markup=reply_markup)
        await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

        return SELECT_GROUPS_STATE

    else:
        await update.message.reply_text(
            "Invalid message, Please use the keys below",
            reply_markup=get_send_tweets_keyboard,
        )
        return GET_SEND_TWEETS_STATE


# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_title = query.data
    user_data = context.user_data.setdefault('selected_titles', [])

    if selected_title in user_data:
        user_data.remove(selected_title)
    else:
        user_data.append(selected_title)

    await query.answer()

    return SELECT_GROUPS_STATE


# Callback query handler
async def get_selected_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proceed = update.message.text
    user_data = context.user_data.get('selected_titles')

    if proceed == BACK_KEY:
        if user_data:
            # Clear the user_data
            context.user_data['selected_titles'] = []

        await update.message.reply_text(
            'Please make sure you get the tweets before sending them to the group(s).',
             reply_markup=get_send_tweets_keyboard,
         )
        return GET_SEND_TWEETS_STATE

    elif proceed == "Proceed":
        if user_data:
            message = "Are you sure you want to send tweets to these group(s):\n\n"

            for index, data in enumerate(user_data, start=1):
                entry = f"{index}. <b>{data}</b>\n"
                message += entry
            await update.message.reply_text(message, reply_markup=send_tweets_keyboard, parse_mode=ParseMode.HTML)
            return SEND_TWEETS_STATE
        else:
            await update.message.reply_text("You haven't selected any group(s).")
    else:
        await update.message.reply_text("Invalid message.")
    return SELECT_GROUPS_STATE


@restricted
@send_action(ChatAction.TYPING)
async def admin_send_tweets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    send = update.message.text
    user_data = context.user_data.get('selected_titles')
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue
    cursor = sqlite_conn.cursor()

    if send == BACK_KEY:
        if user_data:
            # Clear the user_data
            context.user_data['selected_titles'] = []

        cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "No group have been recognised yet.",
                reply_markup=leaderboard_setting_keyboard,
            )
            return LEADERBOARD_SETTING_STATE

        # Create a list to store the inline keyboard buttons
        keyboard = []

        # Iterate through the titles and create a button for each
        for row in rows:
            group_name = row['title']
            if not any(job.name == group_name and job.callback == send_tweets for job in job_queue.jobs()):
                button = InlineKeyboardButton(group_name, callback_data=group_name)
                keyboard.append([button])

        if keyboard == []:
            await update.message.reply_text(
                "Bot is already sending tweets to all group(s).",
                reply_markup=leaderboard_setting_keyboard,
            )
            return LEADERBOARD_SETTING_STATE

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the inline keyboard to the user
        await update.message.reply_text('Select the group(s) to which tweets are to be sent:', reply_markup=reply_markup)
        await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

        return SELECT_GROUPS_STATE

    elif send == "Send 💬":
        if FILE_PATH_ON_SERVER is None:
            context.user_data['selected_titles'] = []
            await update.message.reply_text(
                "You haven't upload an image or GIF for the tweets",
                reply_markup=twitter_keyboard,
            )
            return TWITTER_STATE

        for index, data in enumerate(user_data):
            media = [FILE_PATH_ON_SERVER, USER_UPLOADED_FILE_TYPE, False]
            media.append(data)
            context.job_queue.run_repeating(send_tweets, interval=1800, first=1, chat_id=chat_id, name=str(data), data = media)
            #context.job_queue.run_repeating(send_tweets, interval=10, first=1, chat_id=chat_id, name=str(data), data = media)

        await update.message.reply_text(
            "processing ...",
            reply_markup=get_send_tweets_keyboard,
        )
        return GET_SEND_TWEETS_STATE

@restricted
@send_action(ChatAction.TYPING)
async def stop_get_send_tweet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        'Stop getting and sending tweets\n\n<b><u>Note:</u></b> If you stop getting tweets and all the tweets stored has be sent, no tweets will be sent to the group even if the Bot is still sending tweets to groups',
         reply_markup=stop_get_send_tweets_keyboard,
         parse_mode=ParseMode.HTML,
     )
    return STOP_GET_SEND_TWEETS_STATE


@restricted
@send_action(ChatAction.TYPING)
async def stop_get_tweets_select_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue
    cursor = sqlite_conn.cursor()
    stop_get_send_tweet = update.message.text

    if stop_get_send_tweet == BACK_KEY:
        await update.message.reply_text(
            WELCOME_TO_THE_TWITTER_SECTION,
            reply_markup=twitter_keyboard,
        )
        return TWITTER_STATE

    elif stop_get_send_tweet ==  "Stop Getting Tweets ✋":
        if any(job.callback == get_tweets for job in job_queue.jobs()):
            for job in job_queue.jobs():
                if job.callback == get_tweets:
                    job.schedule_removal()

            await update.message.reply_text(
                "Bot has stopped getting tweets.",
                reply_markup=stop_get_send_tweets_keyboard,
            )
            return STOP_GET_SEND_TWEETS_STATE

        else:
            await update.message.reply_text(
                "The bot is not getting tweets\n\nPlease setup the twitter search keywords, then get and send tweets",
                reply_markup=stop_get_send_tweets_keyboard,
            )
            return STOP_GET_SEND_TWEETS_STATE

    elif stop_get_send_tweet == "Stop Sending Tweets ✋":
        cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "No group have been recognised yet.",
                reply_markup=stop_get_send_tweets_keyboard,
            )
            return STOP_GET_SEND_TWEETS_STATE

        # Create a list to store the inline keyboard buttons
        keyboard = []

        # Iterate through the titles and create a button for each
        for row in rows:
            group_name = row['title']
            if any(job.name == group_name and job.callback == send_tweets for job in job_queue.jobs()):
                button = InlineKeyboardButton(group_name, callback_data=group_name)
                keyboard.append([button])

        if keyboard == []:
            await update.message.reply_text(
                "Bot is not sending tweets to any group(s).",
                reply_markup=stop_get_send_tweets_keyboard,
            )
            return STOP_GET_SEND_TWEETS_STATE

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the inline keyboard to the user
        await update.message.reply_text('Select the group(s) to stop sending tweets:', reply_markup=reply_markup)
        await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

        return SELECT_STOP_GROUPS_STATE

    else:
        await update.message.reply_text(
            "Invalid message, Please use the keys below",
            reply_markup=stop_get_send_tweets_keyboard,
        )
        return STOP_GET_SEND_TWEETS_STATE


# Callback query handler
async def button_callback_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_stop_title = query.data
    user_data = context.user_data.setdefault('selected_stop_titles', [])

    if selected_stop_title in user_data:
        user_data.remove(selected_stop_title)
    else:
        user_data.append(selected_stop_title)

    await query.answer()

    return SELECT_STOP_GROUPS_STATE


# Callback query handler
async def get_selected_groups_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('selected_stop_titles')
    proceed = update.message.text

    if proceed == BACK_KEY:
        if user_data:
            # Clear the user_data
            context.user_data['selected_stop_titles'] = []

        await update.message.reply_text(
            'Stop getting and sending tweets\n\n<b><u>Note:</u></b> If you stop getting tweets and all the tweets stored has be sent, no tweets will be sent to the group even if the Bot is still sending tweets to group(s)',
             reply_markup=stop_get_send_tweets_keyboard,
             parse_mode=ParseMode.HTML,
         )
        return STOP_GET_SEND_TWEETS_STATE

    elif proceed == "Proceed":
        if user_data:
            message = "Are you sure you want to stop sending tweets to these group(s):\n\n"

            for index, data in enumerate(user_data, start=1):
                entry = f"{index}. <b>{data}</b>\n"
                message += entry
            await update.message.reply_text(message, reply_markup=stop_send_tweets_keyboard, parse_mode=ParseMode.HTML)
            return STOP_SEND_TWEETS_STATE
        else:
            await update.message.reply_text("You haven't selected any group(s).")
    else:
        await update.message.reply_text("Invalid message.")
    return SELECT_STOP_GROUPS_STATE


@restricted
@send_action(ChatAction.TYPING)
async def admin_stop_send_tweets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    stop = update.message.text
    user_data = context.user_data.get('selected_stop_titles')
    chat_id = update.effective_message.chat_id
    job_queue = context.job_queue

    if stop == BACK_KEY:
        if user_data:
            # Clear the user_data
            context.user_data['selected_stop_titles'] = []

        cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
        rows = cursor.fetchall()

        if not rows:
            await update.message.reply_text(
                "No group have been recognised yet.",
                reply_markup=stop_get_send_tweets_keyboard,
            )
            return STOP_GET_SEND_TWEETS_STATE

        # Create a list to store the inline keyboard buttons
        keyboard = []

        # Iterate through the titles and create a button for each
        for row in rows:
            group_name = row['title']
            if any(job.name == group_name and job.callback == send_tweets for job in job_queue.jobs()):
                button = InlineKeyboardButton(group_name, callback_data=group_name)
                keyboard.append([button])

        if keyboard == []:
            await update.message.reply_text(
                "Bot is not sending tweets to any group(s).",
                reply_markup=stop_get_send_tweets_keyboard,
            )
            return STOP_GET_SEND_TWEETS_STATE

        # Create the inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the inline keyboard to the user
        await update.message.reply_text('Select the group(s) to stop sending tweets:', reply_markup=reply_markup)
        await update.message.reply_text('Tap or click "Proceed" to continue.', reply_markup=select_group_keyboard)

        return SELECT_STOP_GROUPS_STATE

    elif stop == "Stop Sending Tweets ✋":
        for index, data in enumerate(user_data):
            if any(job.name == data and job.callback == send_tweets for job in job_queue.jobs()):
                for job in job_queue.jobs():
                    if job.name == data and job.callback == send_tweets:
                        job.schedule_removal()

        await update.message.reply_text(
            "Bot has stopped sending tweets to the selected groups.",
            reply_markup=stop_get_send_tweets_keyboard,
        )
        return STOP_GET_SEND_TWEETS_STATE


@restricted
@send_action(ChatAction.TYPING)
async def back_to_home(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> str:
    """get user count"""
    # pylint: disable=unused-argument
    await update.message.reply_text(
        WELCOME_TO_HOME,
        reply_markup=base_keyboard,
    )
    return HOME_STATE

