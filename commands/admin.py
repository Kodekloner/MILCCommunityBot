# encoding: utf-8
import os
import re
import datetime
import time
from logging import getLogger
from dotenv import load_dotenv
from dotenv import set_key

from config.db import sqlite_conn

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from wallet.wallet import mnemonic_to_creds, BSC
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
from constants.states import ADD_ADMIN_STATE
from constants.states import ADMIN_STATE
from constants.states import HOME_STATE
from constants.states import TWITTER_STATE
from constants.states import SEARCH_STATE
from constants.states import SEARCH_DATE_STATE
from constants.states import COMPETITION_STATE
from constants.states import SETUP_POINTS_STATE
from constants.states import INSERT_POINT_STATE
from constants.states import UPDATE_POINT_STATE
from constants.states import LEADERBOARD_SETTING_STATE
from constants.states import TIME_INTERVAL_STATE
from constants.states import STORE_DISPLAY_BOARD_STATE
from constants.states import SETUP_PRIZE_STATE
from constants.states import INSERT_PRIZE_STATE
from constants.states import UPDATE_PRIZE_STATE
from constants.states import PARTICIPANT_STATE
# from constants.states import VIEW_PARTICIPANT_STATE
from constants.states import BAN_PARTICIPANT_STATE
from constants.states import COMFIRM_BAN_PARTICIPANT_STATE
from constants.states import ADMIN_WALLET_STATE
from constants.states import DELETE_WALLET_STATE
# from constants.states import SEND_MESSAGE_TO_ALL_USER
from core.keyboards import admin_keyboard
from core.keyboards import twitter_keyboard
from core.keyboards import competition_keyboard
from core.keyboards import setup_points_keyboard
from core.keyboards import leaderboard_setting_keyboard
from core.keyboards import leaderboard_time_settings_keyboard
from core.keyboards import setup_prize_keyboard
from core.keyboards import participant_keyboard
from core.keyboards import yes_or_no_without_back_key
from core.keyboards import back_keyboard
from core.keyboards import back_to_home_keyboard
from core.keyboards import base_keyboard
from core.keyboards import admin_wallet_keyboard
from utils.decorators import restricted, send_action

from commands.twitter import send_tweets, get_tweets, leaderboard, display_board

# Load environment variables from .env file
load_dotenv()

# Init logger
logger = getLogger(__name__)


async def handle_invalid_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle invalid messages."""
    message = update.message
    reply_text = "I'm sorry, but I didn't understand that command or Message."
    reply_text += "\n\nHere are some suggestions:"
    reply_text += "\n- Please make sure you're using the correct command."
    reply_text += "\n- Use the keys on the keyboard to Send me Message."

    await message.reply_text(reply_text)


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
    )
    return ADMIN_STATE

@restricted
@send_action(ChatAction.TYPING)
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Add an Admin,\nthey will have access to the admin features\n"
        "Send the UserId of the user you want to add.\n"
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
                "Please the UserId is invalid",
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
    )
    return ADMIN_STATE

@restricted
@send_action(ChatAction.TYPING)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM TwitterSearch")
    result = cursor.fetchone()
    if result:
        print(result['word'])
        await update.message.reply_text(
            "These Keywords are been searched already\n\n"
            f"<b><em>{result['word']}</em></b>\n\n"
            "Change the Keywords would you like to search on twitter.\n\n Example:\n MLT OR #MILC OR @MILCplatform\nMLT AND #MILC AND @MILCplatform",
            reply_markup=back_keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            "Set the Keywords would you like to search on twitter.\n\n Example:\n MLT OR #MILC OR @MILCplatform\nMLT AND #MILC AND @MILCplatform",
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
        cursor.execute("UPDATE TwitterCompetitionSearch SET word = ? WHERE id = ?", (message, 1))
        await update.message.reply_text(
            "Search word Updated Successfully, Tap on Send 💬",
            reply_markup=twitter_keyboard,
        )
    else:
        cursor.execute("INSERT INTO TwitterSearch (word) VALUES (?)", (message,))
        cursor.execute("INSERT INTO TwitterCompetitionSearch (word) VALUES (?)", (message,))
        await update.message.reply_text(
            "Search Subject Added Successfully, Tap on Send 💬",
            reply_markup=twitter_keyboard,
        )

    # Commit the changes
    sqlite_conn.commit()

    return TWITTER_STATE

@restricted
@send_action(ChatAction.TYPING)
async def competition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Control the Competition From here",
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
            "You have already set the points,\n To change the point tap on the Change points 📝",
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
        "Control the Competition From here",
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
    from datetime import datetime, timedelta

    chat_id = update.effective_message.chat_id
    # Get the current timestamp

    current_time = datetime.now()

    # Subtract one day from the current timestamp
    previous_day = current_time - timedelta(days=2)

    # Format the previous day as "YYYY-MM-DD"
    # formatted_time = previous_day.strftime("%Y-%m-%d")

    job_queue = context.job_queue

    if any(job.callback == leaderboard for job in job_queue.jobs()):
        await update.message.reply_text(
            "Bot is has already Started Competition",
            reply_markup=competition_keyboard,
        )
        return COMPETITION_STATE

    context.job_queue.run_repeating(leaderboard, interval=86400, first=10, chat_id=chat_id, name=str(chat_id), data=previous_day)

    await update.message.reply_text(
        "Competition Started Successfully",
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
            "Competition Stopped, successfully.",
            reply_markup=competition_keyboard,
        )
        return COMPETITION_STATE
    else:
        await update.message.reply_text(
            "The Competition has not Started Yet. Start the Competition",
            reply_markup=competition_keyboard,
        )
        return COMPETITION_STATE

@restricted
@send_action(ChatAction.TYPING)
async def comp_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please follow the procedure\nFirst Set the time Interval for the leaderboard\nTap on Display\nWhen you want to stop tap on Hide",
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
            f"Time Interval is Currently Set to:\nEvery {value} {time}\n\nUse the Keys below to update the time interval👇",
            reply_markup=leaderboard_time_settings_keyboard,
        )
    else:
        await update.message.reply_text(
            f"Time Interval is Not Set\n\nUse the Keys below to set the time interval👇",
            reply_markup=leaderboard_time_settings_keyboard,
        )
    return TIME_INTERVAL_STATE

@restricted
@send_action(ChatAction.TYPING)
async def set_time_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    time_interval = update.message.text
    if time_interval == "Back ◀️":
        await update.message.reply_text(
            "Please follow the procedure\nFirst Set the time Interval for the leaderboard\nTap on Display\nWhen you want to stop tap on Hide",
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
                f"Time Interval is Currently Set to:\nEvery {value} {time}\n\nUse the Keys below to update the time interval👇",
                reply_markup=leaderboard_time_settings_keyboard,
            )
        else:
            await update.message.reply_text(
                f"Time Interval is Not Set\n\nUse the Keys below to update the time interval👇",
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
                    f"Time Interval has be Successfully updated to:\nEvery {time_interval_value} {time_interval}\n\nGo back to display the leaerboard using the set time interval",
                    reply_markup=leaderboard_time_settings_keyboard,
                )
            else:
                cursor.execute('INSERT INTO leaderboard_time_intervals (time_intervals) VALUES (?)',
                               (interval_message,))
                sqlite_conn.commit()
                await update.message.reply_text(
                    f"Time Interval has be Successfully Set to:\nEvery {time_interval_value} {time_interval}\n\nGo back to display the leaerboard using the set time interval",
                    reply_markup=leaderboard_time_settings_keyboard,
                )

        else:
            await update.message.reply_text(
                f"There was an Issue",
                reply_markup=leaderboard_time_settings_keyboard,
            )
        return TIME_INTERVAL_STATE

@restricted
@send_action(ChatAction.TYPING)
async def display_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM leaderboard_time_intervals")
    result = cursor.fetchone()
    if result:
        chat_id = update.effective_message.chat_id

        job_queue = context.job_queue

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

        if any(job.callback == display_board for job in job_queue.jobs()):
            await update.message.reply_text(
                "The board is been displayed already\n\n If you want to change the time interval,\nChage the Interval, then hide the board and display again\nSo it will be send the leaderboard at the updated time interval.",
                reply_markup=leaderboard_setting_keyboard,
            )
            return LEADERBOARD_SETTING_STATE

        context.job_queue.run_repeating(display_board, interval=seconds, first=5, chat_id=chat_id, name=str(chat_id))

        await update.message.reply_text(
            "The Competition Leaderboard will be displayed at the set time",
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
async def hide_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # chat_id = update.effective_message.chat_id

    job_queue = context.job_queue

    if any(job.callback == display_board for job in job_queue.jobs()):
        for job in job_queue.jobs():
            if job.callback == display_board:
                job.schedule_removal()

        await update.message.reply_text(
            "The Competition Leaderboard will not be displayed again",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE
    else:
        await update.message.reply_text(
            "The Competition leaderboard is not been displayed\n\nSet time interval if you have not\n\nDisplay Leaderboard then hide it any time you want to.",
            reply_markup=leaderboard_setting_keyboard,
        )
        return LEADERBOARD_SETTING_STATE

@restricted
@send_action(ChatAction.TYPING)
async def comp_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        'Manage Participants',
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
        message = "👨‍💼 <b>Participant</b> 👩‍💼\n\n" + message

        await update.message.reply_text(
            message,
            reply_markup=participant_keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.message.reply_text(
            "You don't have a Participant yet",
            reply_markup=participant_keyboard,
        )
    return PARTICIPANT_STATE

@restricted
@send_action(ChatAction.TYPING)
async def ban_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        'Input the Username of the participant you want to ban',
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
            'Manage Participants',
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
            'Manage Participants',
            reply_markup=participant_keyboard,
        )
        return PARTICIPANT_STATE

@restricted
@send_action(ChatAction.TYPING)
async def dis_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Set Prize for Each position in the competition",
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
        await update.message.reply_text(
            "You have already set the Prize,\n To change the prize tap on the Change prize 📝",
            reply_markup=setup_prize_keyboard,
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
        await update.message.reply_text(
            MESSAGE_FOR_CHANGE_PRIZE,
            reply_markup=back_keyboard,
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
        if results:
            message = ""
            for result in results:
                message += f"{result['id']}-{result['token']}\n"

            message += "\n"
            message += "To change the point tap on the Change prize 📝"
            message = "successfully set competition prize\n\n" + message

            await update.message.reply_text(
                message,
                reply_markup=setup_prize_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.message.reply_text(
                SET_PRIZE_SYSTEM,
                reply_markup=setup_prize_keyboard,
            )
        return SETUP_PRIZE_STATE

    else:
        if results:
            await update.message.reply_text(
                MESSAGE_FOR_WRONG_SET_PRIZE,
                reply_markup=setup_prize_keyboard,
            )
            return SETUP_PRIZE_STATE
        else:
            prizes = prizes.strip().split('\n')

            # Check if the input string is valid
            for prize in prizes:
                print(prize)
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
                message += "To change the point tap on the Change prize 📝"
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
        if results:
            message = ""
            for result in results:
                message += f"{result['id']}-{result['token']}\n"

            message += "\n"
            message += "To change the point tap on the Change prize 📝"
            await update.message.reply_text(
                message,
                reply_markup=setup_prize_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.message.reply_text(
                SET_PRIZE_SYSTEM,
                reply_markup=setup_prize_keyboard,
            )
        return SETUP_PRIZE_STATE

    else:
        if results:
            prizes = prizes.strip().split('\n')
            for prize in prizes:
                print(prize)
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

                cursor.execute("UPDATE prize SET token = ? WHERE id = ?", (prize_value, position))
                sqlite_conn.commit()

            cursor.execute("SELECT * FROM prize")
            results = cursor.fetchall()
            message = ""
            for result in results:
                message += f"{result['id']}-{result['token']}\n"

            message += "\n"
            message += "To change the point tap on the Change prize 📝"

            await update.message.reply_text(
                message,
                reply_markup=setup_prize_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
            return SETUP_PRIZE_STATE
        else:
            await update.message.reply_text(
                MESSAGE_FOR_WRONG_CHANGE_PRIZE,
                reply_markup=setup_prize_keyboard,
            )
            return SETUP_prizes_STATE

@restricted
@send_action(ChatAction.TYPING)
async def send_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM prize")
    results = cursor.fetchall()

    if results:
        await update.message.reply_text(
            "Insuffient fonds",
            reply_markup=setup_prize_keyboard,
        )
    else:
        await update.message.reply_text(
            "Set Prize for Each position in the competition.\nBefore send token",
            reply_markup=setup_prize_keyboard,
        )
    return SETUP_PRIZE_STATE

@restricted
@send_action(ChatAction.TYPING)
async def admin_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Get Admin Wallet",
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

        cursor.execute('INSERT INTO admin_wallet (address, private_key, mnemonic) VALUES (?, ?, ?)',
                       (address, private_key, words))
        sqlite_conn.commit()

        await update.message.reply_text(
            "Created Admin Wallet Successfully, View the Wallet details by clicking the button",
            reply_markup=admin_wallet_keyboard,
        )

    else:
        await update.message.reply_text(
            "Admin Wallet already created, View the Wallet details by clicking the button",
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
            "Please Create an Admin wallet first",
            reply_markup=admin_wallet_keyboard,
        )
    else:
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM admin_wallet")
        result = cursor.fetchone()

        # Send the wallet details to the user
        await update.message.reply_text(f"Mnemonic words: {result['mnemonic']}\n\nWallet Address: {result['address']}\n\nPrivate Key: {result['private_key']}",
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
            'Deleted Successfully',
            reply_markup=admin_wallet_keyboard,
        )
        return ADMIN_WALLET_STATE
    elif delete == "No":
        await update.message.reply_text(
            'Admin Wallet',
            reply_markup=admin_wallet_keyboard,
        )
        return ADMIN_WALLET_STATE


@restricted
@send_action(ChatAction.TYPING)
async def add_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Which Date would you like to start searching form on twitter. Example '2023-04-28' without the ''.",
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
            "Search Date Updated Successfully, Now you can now start send tweets",
            reply_markup=twitter_keyboard,
        )
    else:
        cursor.execute("INSERT INTO TwitterSearch (time) VALUES (?)", (message,))
        await update.message.reply_text(
            "Search Date Added Successfully, Now you can now start send tweets",
            reply_markup=twitter_keyboard,
        )

    # Commit the changes
    sqlite_conn.commit()

    return TWITTER_STATE

@restricted
@send_action(ChatAction.TYPING)
async def admin_send_tweets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.excute("SELECT * FROM tweets")
    results = cursor.fetchall()
    if results:
        cursor.execute("DELETE FROM tweets")
        cursor.execute("UPDATE TwitterSearch SET since_id=? WHERE id=?", (None, 1))
        sqlite_conn.commit()

    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_queue = context.job_queue

    if any(job.callback == get_tweets or job.callback == send_tweets for job in job_queue.jobs()):
        await update.message.reply_text(
            "Bot is already Sending Tweets.",
            reply_markup=twitter_keyboard,
        )
        return TWITTER_STATE

    context.job_queue.run_repeating(get_tweets, interval=86400, first=5, chat_id=chat_id, name=str(chat_id))
    # context.job_queue.run_daily(get_tweets, time=datetime.time(23, 30), chat_id=chat_id, name=str(chat_id))
    context.job_queue.run_repeating(send_tweets, interval=600, first=60, chat_id=chat_id, name=str(chat_id))


    await update.message.reply_text(
        "Successful, User will start receciving tweets",
        reply_markup=twitter_keyboard,
    )
    return TWITTER_STATE

@restricted
@send_action(ChatAction.TYPING)
async def stop_tweets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_queue = context.job_queue

    if any(job.callback == get_tweets or job.callback == send_tweets for job in job_queue.jobs()):
        for job in job_queue.jobs():
            if job.callback == get_tweets or job.callback == send_tweets:
                job.schedule_removal()

        await update.message.reply_text(
            "Bot has stopped Sending Tweets.",
            reply_markup=twitter_keyboard,
        )
        return TWITTER_STATE
    else:
        await update.message.reply_text(
            "There is No tweets to stop, Please Setup the twitter Search Subject and date, then send the command to start sending tweets",
            reply_markup=twitter_keyboard,
        )
        return TWITTER_STATE


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
