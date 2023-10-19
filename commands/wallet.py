# encoding: utf-8
import time
from logging import getLogger

from config.db import sqlite_conn

import requests

from web3 import Web3

from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from constants import BACK
from constants.keys import BACK_KEY
from constants.keys import BACK_TO_HOME_KEY
from constants.keys import USER_WALLET_KEY
from constants.messages import SEND_YOUR_MESSAGE
from constants.messages import WELCOME_TO_HOME
from constants.states import HOME_STATE
from constants.states import COMFIRM_LEAVE_COMP_STATE
from constants.states import USER_WALLET_STATE
from constants.states import VIEW_USER_WALLET_STATE
from constants.states import ADD_USER_WALLET_STATE
from constants.states import ADD_USER_WALLET_GROUP_STATE
from constants.states import VIEW_USER_WALLET_DM_STATE
from constants.states import ADD_USERNAME_VIEW_ADDR_DM_STATE
from constants.states import VIEW_USERNAME_ADD_ADDR_DM_STATE
from constants.states import INSERT_USER_GROUP_STATE
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
from core.keyboards import yes_or_no_without_back_key
from core.keyboards import base_keyboard
from core.keyboards import add_user_wallet_keyboard
from core.keyboards import add_user_wallet_group_keyboard
from core.keyboards import view_user_wallet_keyboard
from core.keyboards import change_add_keyboard
from core.keyboards import change_username_keyboard
from core.keyboards import view_user_add_addr_keyboard
from core.keyboards import add_user_view_addr_keyboard
from core.keyboards import view_user_wallet_group_keyboard
from core.keyboards import add_user_view_addr_group_keyboard
from core.keyboards import view_user_add_addr_group_keyboard
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
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "MILC Community Bot allows you to earn rewards by promoting and spreading the word about the MILC project on Twitter. To make this work, the Bot has a competition function and integrated reward distributions.\n"
        "\n"
        "**What's the point of it?**\n"
        "\n"
        "With your help and the incentives that come with it, we want to increase the visibility and reach of the MILC project.\n"
        "\n"
        "You can also take part in the competition to get rewarded.\n\n"
        f"Tap <b>{USER_WALLET_KEY}</b> and follow the instructions.",
        reply_markup=base_keyboard,
        parse_mode=ParseMode.HTML,
    )


@send_action(ChatAction.TYPING)
async def leave_comp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        await update.message.reply_text(
            'Are you sure you want to leave the competition.',
            reply_markup=yes_or_no_without_back_key,
        )
        return COMFIRM_LEAVE_COMP_STATE
    else:
        await update.message.reply_text(
            "You are not in the competition yet.",
            reply_markup=base_keyboard,
        )

@send_action(ChatAction.TYPING)
async def comfirm_leave_comp(update: Update, context: ContextTypes.DEFAULT_TYPE)->str:
    leave = update.message.text
    if leave == "Yes":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        if update.effective_user.username != None:
            telegram_username = update.effective_user.username
        else:
            telegram_username = update.effective_user.first_name
        cursor.execute("DELETE FROM user_wallet_twitter WHERE userid=?", (user_id,),)
        await update.message.reply_text(
            f'You({telegram_username}) have successfully left the competition',
            reply_markup=base_keyboard,
        )
    elif leave == "No":
        await update.message.reply_text(
            'Welcome back',
            reply_markup=base_keyboard,
        )
    return HOME_STATE

@send_action(ChatAction.TYPING)
async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user_id = update.effective_user.id
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()
    if chat.type != Chat.PRIVATE:
        if result:
            if result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "":
                await update.message.reply_text(
                    "View your Twitter username and BSC wallet address",
                    reply_markup=view_user_wallet_keyboard,
                )
                return VIEW_USER_WALLET_STATE
            elif result['twitter_username'] is None or result['twitter_username'] == "" :
                await update.message.reply_text(
                    "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                    reply_markup=add_user_view_addr_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_STATE
            else:
                await update.message.reply_text(
                    "Please add your BSC address",
                    reply_markup=view_user_add_addr_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_STATE

        await update.message.reply_text(
            "Please add your Twitter username and a BSC wallet address to participate in the competition",
            reply_markup=add_user_wallet_keyboard,
        )
        return ADD_USER_WALLET_STATE

    if result:
        if result['twitter_username'] is None or result['twitter_username'] == "" and result['address'] is None or result['address'] == "" :
            await update.message.reply_text(
                "Please add your Twitter username and a BSC wallet address to participate in the competition\n\nYou can change your selected group",
                reply_markup=add_user_wallet_group_keyboard,
            )
            return ADD_USER_WALLET_GROUP_STATE
        elif result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "" :
            await update.message.reply_text(
                "View your Twitter username and BSC wallet address",
                reply_markup=view_user_wallet_group_keyboard,
            )
            return VIEW_USER_WALLET_DM_STATE
        elif result['twitter_username'] is None or result['twitter_username'] == "" :
            await update.message.reply_text(
                "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                reply_markup=add_user_view_addr_group_keyboard,
            )
            return ADD_USERNAME_VIEW_ADDR_DM_STATE
        else:
            await update.message.reply_text(
                "Please add your BSC address",
                reply_markup=view_user_add_addr_group_keyboard,
            )
            return VIEW_USERNAME_ADD_ADDR_DM_STATE

    await update.message.reply_text(
        "Please add your Twitter username and a BSC wallet address to participate in the competition\n\nYou also need to select the group the you recieves the tweets for the competition.",
        reply_markup=add_user_wallet_group_keyboard,
    )
    return ADD_USER_WALLET_GROUP_STATE

@send_action(ChatAction.TYPING)
async def user_select_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT DISTINCT title FROM chat_stats WHERE type LIKE '%group%';")
    rows = cursor.fetchall()

    if not rows:
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            if result['twitter_username'] is None or result['twitter_username'] == "" and result['address'] is None or result['address'] == "" :
                await update.message.reply_text(
                    "There is no group currently",
                    reply_markup=add_user_wallet_group_keyboard,
                )
                return ADD_USER_WALLET_GROUP_STATE
            elif result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "" :
                await update.message.reply_text(
                    "There is no group currently",
                    reply_markup=view_user_wallet_group_keyboard,
                )
                return VIEW_USER_WALLET_DM_STATE
            elif result['twitter_username'] is None or result['twitter_username'] == "" :
                await update.message.reply_text(
                    "There is no group currently",
                    reply_markup=add_user_view_addr_group_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_DM_STATE
            else:
                await update.message.reply_text(
                    "There is no group currently",
                    reply_markup=view_user_add_addr_group_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_DM_STATE

        await update.message.reply_text(
            "There is no group currently",
            reply_markup=add_user_wallet_group_keyboard,
        )
        return ADD_USER_WALLET_GROUP_STATE

    # Create a list to store the inline keyboard buttons
    keyboard = []

    for row in rows:
        group_name = row['title']
        button = InlineKeyboardButton(group_name, callback_data=group_name)
        keyboard.append([button])


    # Create the inline keyboard markup
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the inline keyboard to the user
    await update.message.reply_text('Select the group you are part of as the leaderboard will only be displayed in the group where you receive the tweets:', reply_markup=reply_markup)
    return INSERT_USER_GROUP_STATE

@send_action(ChatAction.TYPING)
async def button_callback_user_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    selected_user_title = query.data
    user_id = update.effective_user.id
    telegram_username = update.effective_user.username
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    ban = False

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
    result = cursor.fetchone()

    await query.answer()

    if not result:
        cursor.execute("INSERT INTO user_wallet_twitter (userid, chat_id, username, telegram_group, ban, first_name) VALUES (?,?,?,?,?,?)", (user_id, chat_id, telegram_username, selected_user_title, ban, first_name))
        sqlite_conn.commit()
        query.edit_message_text(text=f"Successfully selected your group\n\nGroup name: {selected_user_title}")
        return ADD_USER_WALLET_GROUP_STATE

    cursor.execute("UPDATE user_wallet_twitter SET telegram_group = ? WHERE userid = ?", (selected_user_title, user_id))
    sqlite_conn.commit()

    await query.edit_message_text(text=f"Successfully updated your group\n\nGroup name: {selected_user_title}")
    return ADD_USER_WALLET_GROUP_STATE

@send_action(ChatAction.TYPING)
async def add_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Please add one of your BSC wallet address to participate in the competition",
        reply_markup=back_keyboard,
    )
    return STORE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def store_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    address = update.message.text
    if address == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if chat.type != Chat.PRIVATE:
            if result:
                if result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "":
                    await update.message.reply_text(
                        "View your Twitter username and BSC wallet address",
                        reply_markup=view_user_wallet_keyboard,
                    )
                    return VIEW_USER_WALLET_STATE
                elif result['twitter_username'] is None or result['twitter_username'] == "" :
                    await update.message.reply_text(
                        "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                        reply_markup=add_user_view_addr_keyboard,
                    )
                    return ADD_USERNAME_VIEW_ADDR_STATE
                else:
                    await update.message.reply_text(
                        "Please add your BSC address",
                        reply_markup=view_user_add_addr_keyboard,
                    )
                    return VIEW_USERNAME_ADD_ADDR_STATE

            await update.message.reply_text(
                "Please add your Twitter username and a BSC wallet address to participate in the competition",
                reply_markup=add_user_wallet_keyboard,
            )
            return ADD_USER_WALLET_STATE

        if result:
            if result['twitter_username'] is None or result['twitter_username'] == "" and result['address'] is None or result['address'] == "" :
                await update.message.reply_text(
                    "Please add your Twitter username and a BSC wallet address to participate in the competition\n\nYou can change your selected group",
                    reply_markup=add_user_wallet_group_keyboard,
                )
                return ADD_USER_WALLET_GROUP_STATE
            elif result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "" :
                await update.message.reply_text(
                    "View your Twitter username and BSC wallet address",
                    reply_markup=view_user_wallet_group_keyboard,
                )
                return VIEW_USER_WALLET_DM_STATE
            elif result['twitter_username'] is None or result['twitter_username'] == "" :
                await update.message.reply_text(
                    "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                    reply_markup=add_user_view_addr_group_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_DM_STATE
            else:
                await update.message.reply_text(
                    "Please add your BSC address",
                    reply_markup=view_user_add_addr_group_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_DM_STATE

        await update.message.reply_text(
            "Please add your Twitter username and a BSC wallet address to participate in the competition\n\nYou also need to select the group the you recieves the tweets for the competition.",
            reply_markup=add_user_wallet_group_keyboard,
        )
        return ADD_USER_WALLET_GROUP_STATE

    elif verify_bsc_wallet_address(address):
        user_id = update.effective_user.id
        telegram_username = update.effective_user.username
        first_name = update.effective_user.first_name
        chat_id = chat.id
        ban = False
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (address, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, you can now participate in the competition ",
                reply_markup=base_keyboard,
            )
            return HOME_STATE
        else:
            if chat.type != Chat.PRIVATE:
                cursor.execute("INSERT INTO user_wallet_twitter (userid, address, chat_id, username, telegram_group, ban, first_name) VALUES (?,?,?,?,?,?,?)", (user_id, address, chat_id, telegram_username, chat.title, ban, first_name))
            else:
                cursor.execute("INSERT INTO user_wallet_twitter (userid, address, chat_id, username, ban, first_name) VALUES (?,?,?,?,?,?)", (user_id, address, chat_id, telegram_username, ban, first_name))

            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, your wallet address has be saved successfully ✅, enter your twitter username next",
                reply_markup=back_keyboard,
            )
            return STORE_USERNAME_STATE
    else:
        await update.message.reply_text(
            "Invalid address ❌, Please enter a valid BSC address",
            reply_markup=back_keyboard,
        )
        return STORE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def add_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(
        "Register your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
        reply_markup=back_keyboard,
    )
    return STORE_USERNAME_STATE

@send_action(ChatAction.TYPING)
async def store_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    username = update.message.text
    first_name = update.effective_user.first_name
    if username == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if chat.type != Chat.PRIVATE:
            if result:
                if result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "":
                    await update.message.reply_text(
                        "View your Twitter username and BSC wallet address",
                        reply_markup=view_user_wallet_keyboard,
                    )
                    return VIEW_USER_WALLET_STATE
                elif result['twitter_username'] is None or result['twitter_username'] == "" :
                    await update.message.reply_text(
                        "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                        reply_markup=add_user_view_addr_keyboard,
                    )
                    return ADD_USERNAME_VIEW_ADDR_STATE
                else:
                    await update.message.reply_text(
                        "Please add your BSC address",
                        reply_markup=view_user_add_addr_keyboard,
                    )
                    return VIEW_USERNAME_ADD_ADDR_STATE

            await update.message.reply_text(
                "Please add your Twitter username and a BSC wallet address to participate in the competition",
                reply_markup=add_user_wallet_keyboard,
            )
            return ADD_USER_WALLET_STATE

        if result:
            if result['twitter_username'] is None or result['twitter_username'] == "" and result['address'] is None or result['address'] == "" :
                await update.message.reply_text(
                    "Please add your Twitter username and a BSC wallet address to participate in the competition.\n\nYou can change your selected group",
                    reply_markup=add_user_wallet_group_keyboard,
                )
                return ADD_USER_WALLET_GROUP_STATE
            elif result['twitter_username'] is not None and result['twitter_username'] != "" and result['address'] is not None and result['address'] != "" :
                await update.message.reply_text(
                    "View your Twitter username and BSC wallet address",
                    reply_markup=view_user_wallet_group_keyboard,
                )
                return VIEW_USER_WALLET_DM_STATE
            elif result['twitter_username'] is None or result['twitter_username'] == "" :
                await update.message.reply_text(
                    "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                    reply_markup=add_user_view_addr_group_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_DM_STATE
            else:
                await update.message.reply_text(
                    "Please add your BSC address",
                    reply_markup=view_user_add_addr_group_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_DM_STATE

        await update.message.reply_text(
            "Please add your Twitter username and a BSC wallet address to participate in the competition.\n\nYou also need to select the group the you recieves the tweets for the competition.",
            reply_markup=add_user_wallet_group_keyboard,
        )
        return ADD_USER_WALLET_GROUP_STATE
    else:
        user_id = update.effective_user.id
        telegram_username = update.effective_user.username
        chat_id = chat.id
        ban = False

        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (username, user_id))
            await update.message.reply_text(
                "Congratulation!, you can now participate in the competition ",
                reply_markup=base_keyboard,
            )
            return HOME_STATE
        else:
            if chat.type != Chat.PRIVATE:
                cursor.execute("INSERT INTO user_wallet_twitter (userid, twitter_username, chat_id, username, telegram_group, ban, first_name) VALUES (?,?,?,?,?,?,?)", (user_id, username, chat_id, telegram_username, chat.title, ban, first_name))
            else:
                cursor.execute("INSERT INTO user_wallet_twitter (userid, twitter_username, chat_id, username, ban, first_name) VALUES (?,?,?,?,?,?)", (user_id, username, chat_id, telegram_username, ban, first_name))

            await update.message.reply_text(
                "Congratulation!, your Twitter username was added successfully. Add your address if you haven't",
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
        f"Your wallet address is {result['address']}",
        reply_markup=change_add_keyboard,
    )
    return OPT_CHANGE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def opt_change_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    message = update.message.text
    if message == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if chat.type != Chat.PRIVATE:
            if result['twitter_username'] == "" or result['twitter_username'] is None:
                await update.message.reply_text(
                    "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                    reply_markup=add_user_view_addr_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_STATE
            else:
                await update.message.reply_text(
                    "View your Twitter username and BSC wallet address",
                    reply_markup=view_user_wallet_keyboard,
                )
                return VIEW_USER_WALLET_STATE

        if result['twitter_username'] == "" or result['twitter_username'] is None:
            await update.message.reply_text(
                "Type your Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
                reply_markup=add_user_view_addr_group_keyboard,
            )
            return ADD_USERNAME_VIEW_ADDR_DM_STATE
        else:
            await update.message.reply_text(
                "View your Twitter username and BSC wallet address",
                reply_markup=view_user_wallet_group_keyboard,
            )
            return VIEW_USER_WALLET_DM_STATE

    elif message == "Change Address 💲":
        await update.message.reply_text(
            "Type your new BSC address",
            reply_markup=back_keyboard,
        )
        return CHANGE_ADDRESS_STATE
    else:
        await update.message.reply_text(
            f"Invalid command",
            reply_markup=change_add_keyboard,
        )
        return OPT_CHANGE_ADDRESS_STATE

@send_action(ChatAction.TYPING)
async def store_change_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    message = update.message.text
    if message == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        await update.message.reply_text(
            f"Your wallet is {result['address']}",
            reply_markup=change_add_keyboard,
        )
        return OPT_CHANGE_ADDRESS_STATE
    elif verify_bsc_wallet_address(message):
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if chat.type != Chat.PRIVATE:
            if result['twitter_username'] == "" or result['twitter_username'] is None:
                cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (message, user_id))
                sqlite_conn.commit()
                await update.message.reply_text(
                    "Congratulation!, you have successfully changed your BSC wallet address. Add your Twitter Username if you haven't",
                    reply_markup=add_user_view_addr_keyboard,
                )
                return ADD_USERNAME_VIEW_ADDR_STATE
            else:
                cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (message, user_id))
                sqlite_conn.commit()
                await update.message.reply_text(
                    "Congratulation!, you have successfully changed your BSC wallet address. Be active on Twitter to get free MLT tokens",
                    reply_markup=view_user_wallet_keyboard,
                )
                return VIEW_USER_WALLET_STATE

        if result['twitter_username'] == "" or result['twitter_username'] is None:
            cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, you have successfully changed your BSC wallet address. Add your Twitter username if you haven't",
                reply_markup=add_user_view_addr_group_keyboard,
            )
            return ADD_USERNAME_VIEW_ADDR_DM_STATE
        else:
            cursor.execute("UPDATE user_wallet_twitter SET address = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, you have successfully changed your BSC wallet address. Be active on Twitter to get free MLT tokens",
                reply_markup=view_user_wallet_group_keyboard,
            )
            return VIEW_USER_WALLET_DM_STATE
    else:
        await update.message.reply_text(
            "Invalid address ❌, please enter a valid BSC Address",
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
    chat = update.effective_chat
    message = update.message.text
    if message == "Back ◀️":
        user_id = update.effective_user.id
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user_wallet_twitter WHERE userid = ?", (user_id,))
        result = cursor.fetchone()
        if chat.type != Chat.PRIVATE:
            if result['address'] == "" or result['address'] is None:
                await update.message.reply_text(
                    "You have not added your BSC wallet address",
                    reply_markup=view_user_add_addr_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_STATE
            else:
                await update.message.reply_text(
                    "View your Twitter username and BSC wallet address",
                    reply_markup=view_user_wallet_keyboard,
                )
                return VIEW_USER_WALLET_STATE

        if result['address'] == "" or result['address'] is None:
            await update.message.reply_text(
                "You have not added your BSC wallet address",
                reply_markup=view_user_add_addr_group_keyboard,
            )
            return VIEW_USERNAME_ADD_ADDR_DM_STATE
        else:
            await update.message.reply_text(
                "View your Twitter username and BSC wallet address",
                reply_markup=view_user_wallet_group_keyboard,
            )
            return VIEW_USER_WALLET_DM_STATE

    elif message == "Change Twitter username 👨‍💼":
        await update.message.reply_text(
            "Type your new Twitter username - without @ and case sensitive - for example: weezel87 or nvaiotelli",
            reply_markup=back_keyboard,
        )
        return CHANGE_USERNAME_STATE
    else:
        await update.message.reply_text(
            f"Invalid command {message}",
            reply_markup=change_username_keyboard,
        )
        return OPT_CHANGE_USERNAME_STATE

@send_action(ChatAction.TYPING)
async def store_change_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
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
        if chat.type != Chat.PRIVATE:
            if result['address'] == "" or result['address'] is None:
                cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (message, user_id))
                sqlite_conn.commit()
                await update.message.reply_text(
                    "Congratulation!, you have successfully changed your twitter username. Add your BSC wallet address if you haven't",
                    reply_markup=view_user_add_addr_keyboard,
                )
                return VIEW_USERNAME_ADD_ADDR_STATE
            else:
                cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (message, user_id))
                sqlite_conn.commit()
                await update.message.reply_text(
                    "Congratulation!, you have successfully changed your twitter username. Be active on Twitter to get free MLT tokens",
                    reply_markup=view_user_wallet_keyboard,
                )
                return VIEW_USER_WALLET_STATE

        if result['address'] == "" or result['address'] is None:
            cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, you have successfully changed your twitter username. Add your address if you haven't",
                reply_markup=view_user_add_addr_group_keyboard,
            )
            return VIEW_USERNAME_ADD_ADDR_DM_STATE
        else:
            cursor.execute("UPDATE user_wallet_twitter SET twitter_username = ? WHERE userid = ?", (message, user_id))
            sqlite_conn.commit()
            await update.message.reply_text(
                "Congratulation!, you have successfully changed your twitter username. Be active on Twitter to get free MLT tokens",
                reply_markup=view_user_wallet_group_keyboard,
            )
            return VIEW_USER_WALLET_DM_STATE

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
