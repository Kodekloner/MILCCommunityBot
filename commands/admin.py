# encoding: utf-8
import datetime
import time
from logging import getLogger

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
from constants.states import ADMIN_STATE
from constants.states import HOME_STATE
from constants.states import TWITTER_STATE
from constants.states import SEARCH_STATE
from constants.states import SEARCH_DATE_STATE
from constants.states import COMPETITION_STATE
from constants.states import ADMIN_WALLET_STATE
# from constants.states import SEND_MESSAGE_TO_ALL_USER
from core.keyboards import admin_keyboard
from core.keyboards import twitter_keyboard
from core.keyboards import competition_keyboard
from core.keyboards import back_keyboard
from core.keyboards import base_keyboard
from core.keyboards import admin_wallet_keyboard
from utils.decorators import restricted, send_action

from commands.twitter import send_tweets, get_tweets, leaderboard

# Init logger
logger = getLogger(__name__)


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
    await update.message.reply_text(
        "Which Subject would you like to search on twitter. Example 'MLT #MILC @MILCplatform' without the ''.",
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
            "Search word Updated Successfully, Setup The Date it will start searching from",
            reply_markup=twitter_keyboard,
        )
    else:
        cursor.execute("INSERT INTO TwitterSearch (word) VALUES (?)", (message,))
        await update.message.reply_text(
            "Search Subject Added Successfully, Setup The Date it will start searching from",
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
async def star_comp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    from datetime import datetime, timedelta

    chat_id = update.effective_message.chat_id
    # Get the current timestamp

    current_time = datetime.now()

    # Subtract one day from the current timestamp
    previous_day = current_time - timedelta(days=1)

    # Format the previous day as "YYYY-MM-DD"
    formatted_time = previous_day.strftime("%Y-%m-%d")

    job_queue = context.job_queue

    if any(job.callback == leaderboard for job in job_queue.jobs()):
        await update.message.reply_text(
            "Bot is has already Started Competition",
            reply_markup=competition_keyboard,
        )
        return COMPETITION_STATE

    context.job_queue.run_repeating(leaderboard, interval=1800, first=10, chat_id=chat_id, name=str(chat_id), data=formatted_time)

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
async def dis_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass

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
        # print(f'{private_key=}')
        # print(f'{address=}')

        # Construct from private_key and address
        wallet = BSC(private_key, address)

        # Get wallet balance
        balance = wallet.balance()
        # print(f'{balance=}')

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
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    job_queue = context.job_queue

    if any(job.callback == get_tweets or job.callback == send_tweets for job in job_queue.jobs()):
        await update.message.reply_text(
            "Bot is already Sending Tweets.",
            reply_markup=twitter_keyboard,
        )
        return TWITTER_STATE

    context.job_queue.run_daily(get_tweets, time=datetime.time(23, 30), chat_id=chat_id, name=str(chat_id))
    context.job_queue.run_repeating(send_tweets, interval=30, first=10, chat_id=chat_id, name=str(chat_id))

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
