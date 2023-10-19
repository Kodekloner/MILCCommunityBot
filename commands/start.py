import time
from datetime import datetime
from datetime import timezone
from logging import getLogger

from telegram import Update
from telegram.constants import ChatAction
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler

from constants import NO
from constants import YES
from constants.keys import BACK_KEY
from constants.messages import GOODBYE_WE_ARE_SORRY
from constants.messages import PRIVACY_MESSAGE
from constants.messages import WELCOME_MESSAGE
from constants.states import HOME_STATE
from core.keyboards import base_keyboard
from utils.decorators import send_action

logger = getLogger(__name__)


@send_action(ChatAction.TYPING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: Adding parent/child or show data."""
    # pylint: disable=unused-argument
    message = update.message.text
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    username = update.effective_user.username
    if message == NO:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=GOODBYE_WE_ARE_SORRY.format(first_name=first_name),
        )
        return ConversationHandler.END
    elif message == YES:
        # create_user(user_id, first_name, last_name, username)
        await update.message.reply_text(
            WELCOME_MESSAGE.format(first_name=first_name),
            reply_markup=base_keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )
        return HOME_STATE
    else:
        """Handle invalid messages."""
        message = update.message
        reply_text = "I'm sorry, but I didn't understand that command or Message."
        reply_text += "\n\nHere are some suggestions:"
        reply_text += "\n- Use the keys on the keyboard to Send me Message."

        await message.reply_text(reply_text)
