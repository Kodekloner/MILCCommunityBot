import time
import numpy as np

# from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from logging import getLogger
from wallet.wallet import BSC
# from time import sleep

import commands
from config.db import sqlite_conn
from config import logger


# from config.options import config

# Init logger
logger = getLogger(__name__)

async def send_tokens(reciever_address, token):
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM admin_wallet")
    result = cursor.fetchone()

    if result:
        # Construct from private_key and address
        wallet = BSC(result['private_key'], result['address'])

        # result, message = wallet.send_transaction(reciever_address, token)
        result, message = wallet.send_token_transaction(reciever_address, token)
        return result, message



async def distribute_token_winners(group, chat_id, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor = sqlite_conn.cursor()
    cursor.execute(
        """
        SELECT uwt.username, uwt.twitter_username, uwt.address, uwt.chat_id, COALESCE(l.total, 0) AS total
        FROM user_wallet_twitter uwt
        LEFT JOIN leaderboard l ON uwt.twitter_username = l.username
        WHERE uwt.ban = ? AND uwt.telegram_group = ? AND uwt.address IS NOT NULL AND uwt.address <> ''
        ORDER BY l.total DESC
        """,
        (False, group),
    )

    participants = cursor.fetchall()

    # if participates:
    #     print(np.array(rows))

    # Retrieve the prize data
    prize_query = "SELECT id, token FROM prize ORDER BY id ASC;"

    # Execute the prize query and fetch all rows
    cursor.execute(prize_query)
    prize_data = cursor.fetchall()

    reply_message = ""

    # Iterate over the participants and distribute tokens
    for index, participant in enumerate(participants):
        # Check if the participant is eligible for a prize based on the prize table
        if index < len(prize_data):
            prize_id, token = prize_data[index]
            # Distribute tokens to the participant using their address
            result, message = await send_tokens(participant['address'], token)
            # You can also store the prize_id and other details in the database for record-keeping

            if result:
                entry = f"{index+1}. Transfer of {token} to {participant['username']} with a total score of {participant['total']} and address of {participant['address']} was <b>Successful</b>\n<b>Transaction hash: {message}</b>\n\n"
                reply_message += entry
                cursor.execute('INSERT INTO transactions (usersame, address, total, amount, status) VALUES (?, ?, ?, ?,?)',
                               (participant['username'], participant['address'], participant['total'], token, f"Transaction successful! Transaction hash: {message}"))
                sqlite_conn.commit()
            else:
                entry = f"{index+1}. Transfer of {token} to {participant['username']} with a total score of {participant['total']} and address of {participant['address']} <b>failed</b>\n<b>Failed: {message}</b>\n\n"
                reply_message += entry
                cursor.execute('INSERT INTO transactions (usersame, address, total, amount, status) VALUES (?, ?, ?, ?,?)',
                               (participant['username'], participant['address'], participant['total'], token, f"Transaction failed: {message}"))
                sqlite_conn.commit()

            time.sleep(60)

    reply_message = "<b>Transaction Status</b>\n\n" + reply_message

    await context.bot.send_message(chat_id,
        text=reply_message,
        parse_mode=ParseMode.HTML,
    )
