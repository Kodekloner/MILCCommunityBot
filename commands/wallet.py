# encoding: utf-8
import time
from logging import getLogger

from config.db import sqlite_conn

import requests

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
from constants.states import STORE_USERNAME_STATE
from constants.states import VIEW_ADDRESS_STATE
from constants.states import VIEW_USERNAME_STATE
from constants.states import CHANGE_USERNAME_STATE
from constants.states import CHANGE_ADDRESS_STATE
from constants.states import ADD_USERNAME_VIEW_ADDR_STATE
from constants.states import VIEW_USERNAME_ADD_ADDR_STATE
from constants.states import OPT_CHANGE_USERNAME_STATE
from constants.states import OPT_CHANGE_ADDRESS_STATE
from core.keyboards import back_keyboard
from core.keyboards import base_keyboard
from core.keyboards import add_user_wallet_keyboard
from core.keyboards import view_user_wallet_keyboard
from core.keyboards import change_add_keyboard
from core.keyboards import change_username_keyboard
from core.keyboards import view_user_add_addr_keyboard
from core.keyboards import add_user_view_addr_keyboard
from utils.decorators import send_action

# Init logger
logger = getLogger(__name__)



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
        if result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "" :
            await update.message.reply_text(
                "View your Twitter username and BSC wallet address",
                reply_markup=view_user_wallet_keyboard,
            )
            return VIEW_USER_WALLET_STATE
        elif result['twitter_username'] is None or result['twitter_username'] == "" :
            await update.message.reply_text(
                "Add your Twitter Username",
                reply_markup=add_user_view_addr_keyboard,
            )
            return ADD_USERNAME_VIEW_ADDR_STATE
        else:
            await update.message.reply_text(
                "Please Add your BSC Address",
                reply_markup=view_user_add_addr_keyboard,
            )
            return VIEW_USERNAME_ADD_ADDR_STATE

    await update.message.reply_text(
        "Please add your Twitter username and a BSC wallet address to participate in the competition",
        reply_markup=add_user_wallet_keyboard,
    )
    return ADD_USER_WALLET_STATE

@send_action(ChatAction.TYPING)
async def add_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please add one of your BSC wallet address to participate in the competition",
        reply_markup=back_keyboard,
    )
    return STORE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def store_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    address = update.message.text
    if address == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            if result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "" :
                await update.message.reply_text(
                    "View your Twitter username and BSC wallet address",
                    reply_markup=view_user_wallet_keyboard,
                )
                return VIEW_USER_WALLET_STATE
            elif result['twitter_username'] is None or result['twitter_username'] == "" :
                await update.message.reply_text(
                    "Add your Twitter Username",
                    reply_markup=add_user_view_addr_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_STATE
            else:
                await update.message.reply_text(
                    "Please Add your BSC Address",
                    reply_markup=view_user_add_addr_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_STATE

        await update.message.reply_text(
            "Please add your Twitter username and a BSC wallet address to participate in the competition",
            reply_markup=add_user_wallet_keyboard,
        )
        return ADD_USER_WALLET_STATE

    elif verify_bsc_wallet_address(address):
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            # if result['twitter_username'] is not None and result['twitter_username'] != "" :
            cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (address, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, You can Now Participate in the Competition ",
                reply_markup=base_keyboard,
            )
            return HOME_STATE
            # else:
            #     cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (address, user_id))
            #     sqlite_conn.commit()
            #     await update.message.reply_text(
            #         "Please add your Twitter Username",
            #         reply_markup=back_keyboard,
            #     )
            #     return STORE_USERNAME_STATE
        else:
            cursor.execute("INSERT INTO user_wallet_twitter (userid, address) VALUES (?,?)", (user_id, address))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, Your Wallet address has be saved successfully ✅, Enter Your Twitter username Next",
                reply_markup=back_keyboard,
            )
            return STORE_USERNAME_STATE
    else:
        await update.message.reply_text(
            "Invalid Address ❌, Please Enter a Valid BSC Address",
            reply_markup=back_keyboard,
        )
        return STORE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def add_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please add your Twitter Username",
        reply_markup=back_keyboard,
    )
    return STORE_USERNAME_STATE

@send_action(ChatAction.TYPING)
async def store_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    username = update.message.text
    if username == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            if result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "" :
                await update.message.reply_text(
                    "View your Twitter username and BSC wallet address",
                    reply_markup=view_user_wallet_keyboard,
                )
                return VIEW_USER_WALLET_STATE
            elif result['twitter_username'] is None or result['twitter_username'] == "" :
                await update.message.reply_text(
                    "Add your Twitter Username",
                    reply_markup=add_user_view_addr_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_STATE
            else:
                await update.message.reply_text(
                    "Please Add your BSC Address",
                    reply_markup=view_user_add_addr_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_STATE

        await update.message.reply_text(
            "Please add your Twitter username and a BSC wallet address to participate in the competition",
            reply_markup=add_user_wallet_keyboard,
        )
        return ADD_USER_WALLET_STATE
    else:
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            # if result['address'] is not None and result['address'] != None :
            cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (username, user_id))
            await update.message.reply_text(
                "Congratulation!, You can Now Participate in the Competition ",
                reply_markup=base_keyboard,
            )
            return HOME_STATE
            # else:
            #     cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (username, user_id))
            #     await update.message.reply_text(
            #         "Please add one of your BSC wallet address to participate in the competition",
            #         reply_markup=back_keyboard,
            #     )
            #     return STORE_ADDRESS_STATE
        else:
            cursor.execute("INSERT INTO user_wallet_twitter (userid, twitter_username) VALUES (?,?)", (user_id, username))
            await update.message.reply_text(
                "Congratulation!, your Twitter username was added Successfully. Add your Address if you haven't",
                reply_markup=back_keyboard,
            )
            return STORE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def view_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    await update.message.reply_text(
        f"Your Wallet Address is {result['address']}",
        reply_markup=change_add_keyboard,
    )
    return OPT_CHANGE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def opt_change_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.message.text
    if message == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result['twitter_username'] == "" or result['twitter_username'] is None:
            await update.message.reply_text(
                "Add your Twitter Username",
                reply_markup=add_user_view_addr_keyboard,
            )
            return ADD_USERNAME_VIEW_ADDR_STATE
        else:
            await update.message.reply_text(
                "View your Twitter username and BSC wallet address",
                reply_markup=view_user_wallet_keyboard,
            )
            return VIEW_USER_WALLET_STATE

    elif message == "Change Address 💲":
        await update.message.reply_text(
            "Type Your new BSC Address",
            reply_markup=back_keyboard,
        )
        return CHANGE_ADDRESS_STATE
    else:
        await update.message.reply_text(
            f"Invalid Command",
            reply_markup=change_add_keyboard,
        )
        return OPT_CHANGE_ADDRESS_STATE

async def store_change_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.message.text
    if message == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        await update.message.reply_text(
            f"Your username is {result['address']}",
            reply_markup=change_add_keyboard,
        )
        return OPT_CHANGE_ADDRESS_STATE
    elif verify_bsc_wallet_address(message):
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result['twitter_username'] == "" or result['twitter_username'] is None:
            cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, You have Successfully changed your BSC Wallet Address. Add your Twitter Username if you haven't",
                reply_markup=add_user_view_addr_keyboard,
            )
            return ADD_USERNAME_VIEW_ADDR_STATE
        else:
            cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, You have Successfully changed your BSC Wallet Address. Be active on Twitter to get Free MLT tokens",
                reply_markup=view_user_wallet_keyboard,
            )
            return VIEW_USER_WALLET_STATE
    else:
        await update.message.reply_text(
            "Invalid Address ❌, Please Enter a Valid BSC Address",
            reply_markup=back_keyboard,
        )
        return CHANGE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def view_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    await update.message.reply_text(
        f"Your Twitter username is {result['twitter_username']}",
        reply_markup=change_username_keyboard,
    )
    return OPT_CHANGE_USERNAME_STATE

@send_action(ChatAction.TYPING)
async def opt_change_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.message.text
    if message == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result['address'] == "" or result['address'] is None:
            await update.message.reply_text(
                "You have not Added your BSC wallet Address",
                reply_markup=view_user_add_addr_keyboard,
            )
            return VIEW_USERNAME_ADD_ADDR_STATE
        else:
            await update.message.reply_text(
                "View your Twitter username and BSC wallet address",
                reply_markup=view_user_wallet_keyboard,
            )
            return VIEW_USER_WALLET_STATE

    elif message == "Change Twitter username 👨‍💼":
        await update.message.reply_text(
            "Type Your new Username",
            reply_markup=back_keyboard,
        )
        return CHANGE_USERNAME_STATE
    else:
        await update.message.reply_text(
            f"Invalid Command {message}",
            reply_markup=change_username_keyboard,
        )
        return OPT_CHANGE_USERNAME_STATE

@send_action(ChatAction.TYPING)
async def store_change_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.message.text
    if message == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        await update.message.reply_text(
            f"Your username is {result['twitter_username']}",
            reply_markup=change_username_keyboard,
        )
        return OPT_CHANGE_USERNAME_STATE
    else:
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result['address'] == "" or result['address'] is None:
            cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, You have Successfully changed your twitter username. Add your Address if you haven't",
                reply_markup=view_user_add_addr_keyboard,
            )
            return VIEW_USERNAME_ADD_ADDR_STATE
        else:
            cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, You have Successfully changed your twitter username. Be active on Twitter to get Free MLT tokens",
                reply_markup=view_user_wallet_keyboard,
            )
            return VIEW_USER_WALLET_STATE


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
