# encoding: utf-8
import time
from logging import getLogger

from config.db import sqlite_conn

from web3 import Web3

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from constants import BACK
from constants.keys import BACK_KEY
from constants.keys import BACK_TO_HOME_KEY
from constants.messages import SEND_YOUR_MESSAGE
from constants.messages import WELCOME_TO_HOME
from constants.states import HOME_STATE
from constants.states import USER_WALLET_STATE
from constants.states import VIEW_USER_WALLET_STATE
from constants.states import ADD_USER_WALLET_STATE
from constants.states import STORE_ADDRESS_STATE
from constants.states import STORE_PASS_STATE
from constants.states import STORE_USERNAME_STATE
from constants.states import VIEW_ADDRESS_STATE
from constants.states import VIEW_PASS_STATE
from constants.states import VIEW_USERNAME_STATE
from constants.states import CHANGE_USERNAME_STATE
from constants.states import CHANGE_PASS_STATE
from constants.states import CHANGE_ADDRESS_STATE
from core.keyboards import back_keyboard
from core.keyboards import base_keyboard
from core.keyboards import add_user_wallet_keyboard
from core.keyboards import add_address_keyboard
from core.keyboards import view_user_wallet_keyboard
from core.keyboards import change_add_keyboard
from core.keyboards import change_pass_keyboard
from core.keyboards import change_username_keyboard
from utils.decorators import send_action

# Init logger
logger = getLogger(__name__)

twitter_login = {}

def validate_twitter_user(twitter_login):
    pass

def verify_bsc_wallet_address(address):
    # Connect to the BSC network using a Web3 provider
    w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))  # Use an appropriate BSC node URL

    # Check if the address is a valid BSC checksum address
    if w3.is_address(address):
        return True
    else:
        return False

@send_action(ChatAction.TYPING)
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        await update.message.reply_text(
            "View your Twitter username, password and a BSC wallet address",
            reply_markup=view_user_wallet_keyboard,
        )
        return VIEW_USER_WALLET_STATE
    await update.message.reply_text(
        "Please add your Twitter username and a BSC wallet address to participate in the competition",
        reply_markup=add_user_wallet_keyboard,
    )
    return ADD_USER_WALLET_STATE

@send_action(ChatAction.TYPING)
async def add_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please add one of your BSC wallet address to participate in the competition",
        reply_markup=add_address_keyboard,
    )
    return STORE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def store_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    address = update.message.text
    if address == "Back ◀️":
        await update.message.reply_text(
                "Please add your Twitter username and a BSC wallet address to participate in the competition",
                reply_markup=add_user_wallet_keyboard,
            )
        return ADD_USER_WALLET_STATE

    elif verify_bsc_wallet_address(address):
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("INSERT INTO user_wallet_twitter (userid, address) VALUES (?,?)", (user_id, address))
        sqlite_conn.commit()
        await update.message.reply_text(
            "Your Wallet address has be saved successfully ✅, Enter Your Twitter Login Details Next",
            reply_markup=add_user_wallet_keyboard,
        )
        return ADD_USER_WALLET_STATE
    else:
        await update.message.reply_text(
            "Invalid Address ❌, Please Enter a Valid BSC Address",
            reply_markup=add_address_keyboard,
        )
        return STORE_ADDRESS_STATE

    await update.message.reply_text(
        "Please add one of your BSC wallet address to participate in the competition",
        reply_markup=twitter_username_keyboard,
    )
    return STORE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def add_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please add your Twitter Username",
        reply_markup=add_address_keyboard,
    )
    return STORE_USERNAME_STATE

@send_action(ChatAction.TYPING)
async def store_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    username = update.message.text
    if username == "Back ◀️":
        await update.message.reply_text(
                "Please add your Twitter username and a BSC wallet address to participate in the competition",
                reply_markup=add_user_wallet_keyboard,
            )
        return ADD_USER_WALLET_STATE
    else:
        twitter_login['username'] = username
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            if "pass" in twitter_login:
                if validate_twitter_user(twitter_login):
                    cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (username, user_id))
                    await update.message.reply_text(
                        "Congratulation!, your Twitter details are correct. Add your Address if you haven't",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
                else:
                    await update.message.reply_text(
                        "Either your username or password is wrong",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
            else:
                await update.message.reply_text(
                    "Enter Your Twitter Password",
                    reply_markup=add_user_wallet_keyboard,
                )
                return ADD_USER_WALLET_STATE
        else:
            if "pass" in twitter_login:
                if validate_twitter_user(twitter_login):
                    cursor.execute("INSERT INTO user_wallet_twitter (userid, twitter_username) VALUES (?,?)", (user_id, username))
                    await update.message.reply_text(
                        "Congratulation!, your Twitter details are correct. Add your Address if you haven't",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
                else:
                    await update.message.reply_text(
                        "Either your username or password is wrong",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
            else:
                await update.message.reply_text(
                    "Enter Your Twitter Password",
                    reply_markup=add_user_wallet_keyboard,
                )
                return ADD_USER_WALLET_STATE

@send_action(ChatAction.TYPING)
async def add_pass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please add your Twitter Password",
        reply_markup=add_address_keyboard,
    )
    return STORE_PASS_STATE

@send_action(ChatAction.TYPING)
async def store_pass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    password = update.message.text
    if password == "Back ◀️":
        await update.message.reply_text(
                "Please add your Twitter username and a BSC wallet address to participate in the competition",
                reply_markup=add_user_wallet_keyboard,
            )
        return ADD_USER_WALLET_STATE
    else:
        twitter_login['pass'] = password
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            if "username" in twitter_login:
                if validate_twitter_user(twitter_login):
                    cursor.execute("UPDATE user_wallet_twitter SET twitter_pass = ? WHERE userid = ?", (password, user_id))
                    await update.message.reply_text(
                        "Congratulation!, your Twitter details are correct. Add your Address if you haven't",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
                else:
                    await update.message.reply_text(
                        "Either your username or password is wrong",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
            else:
                await update.message.reply_text(
                    "Enter Your Twitter Username",
                    reply_markup=add_user_wallet_keyboard,
                )
                return ADD_USER_WALLET_STATE
        else:
            if "username" in twitter_login:
                if validate_twitter_user(twitter_login):
                    cursor.execute("INSERT INTO user_wallet_twitter (userid, twitter_pass) VALUES (?,?)", (user_id, password))
                    await update.message.reply_text(
                        "Congratulation!, your Twitter details are correct. Add your Address if you haven't",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
                else:
                    await update.message.reply_text(
                        "Either your username or password is wrong",
                        reply_markup=add_user_wallet_keyboard,
                    )
                    return ADD_USER_WALLET_STATE
            else:
                await update.message.reply_text(
                    "Enter Your Twitter Username",
                    reply_markup=add_user_wallet_keyboard,
                )
                return ADD_USER_WALLET_STATE

@send_action(ChatAction.TYPING)
async def view_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    if result['address'] == "":
        await update.message.reply_text(
            "Please add one of your BSC wallet address to participate in the competition",
            reply_markup=add_address_keyboard,
        )
        return STORE_ADDRESS_STATE
    else:
        await update.message.reply_text(
            f"your username is {result['address']}",
            reply_markup=change_add_keyboard,
        )
        return CHANGE_add_STATE


@send_action(ChatAction.TYPING)
async def dis_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass

@send_action(ChatAction.TYPING)
async def view_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    if result['twitter_username'] == "":
        await update.message.reply_text(
            "Please add your Twitter Username",
            reply_markup=add_address_keyboard,
        )
        return STORE_USERNAME_STATE
    else:
        await update.message.reply_text(
            f"your username is {result['twitter_username']}",
            reply_markup=change_username_keyboard,
        )
        return CHANGE_USERNAME_STATE

@send_action(ChatAction.TYPING)
async def dis_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass

@send_action(ChatAction.TYPING)
async def view_pass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    if result['twitter_pass'] == "":
        await update.message.reply_text(
            "Please add your Twitter Password",
            reply_markup=add_address_keyboard,
        )
        return STORE_PASS_STATE
    else:
        await update.message.reply_text(
            f"your username is {result['twitter_pass']}",
            reply_markup=change_pass_keyboard,
        )
        return CHANGE_PASS_STATE

@send_action(ChatAction.TYPING)
async def dis_pass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass

# @send_action(ChatAction.TYPING)
# async def twitter_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     await update.message.reply_text(
#         "Please add your Twitter username and a BSC wallet address to participate in the competition",
#         reply_markup=twitter_username_keyboard,
#     )
#     return USER_WALLET_STATE

# @send_action(ChatAction.TYPING)
# async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     await update.message.reply_text(
#         "Please add your Twitter username and a BSC wallet address to participate in the competition",
#         reply_markup=user_wallet_keyboard,
#     )
#     return USER_WALLET_STATE

# @send_action(ChatAction.TYPING)
# async def back_to_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
#     user_id = update.effective_user.id
#     cursor = sqlite_conn.cursor()
#     cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
#     result = cursor.fetchone()
#     if result:
#         await update.message.reply_text(
#             "View your Twitter username, password and a BSC wallet address",
#             reply_markup=view_user_wallet_keyboard,
#         )
#         return VIEW_USER_WALLET_STATE
#     await update.message.reply_text(
#         "Please add your Twitter username and a BSC wallet address to participate in the competition",
#         reply_markup=add_user_wallet_keyboard,
#     )
#     return ADD_USER_WALLET_STATE
#
#     await update.message.reply_text(
#         WELCOME_TO_HOME,
#         reply_markup=base_keyboard,
#     )
#     return HOME_STATE


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
