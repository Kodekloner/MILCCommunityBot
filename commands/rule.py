import management
from logging import getLogger

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes, ConversationHandler


from constants.messages import PRIVACY_MESSAGE
from constants.messages import RULE_MESSAGE
from constants.messages import WELCOME_MESSAGE, WELCOME_MESSAGE_BACK
from constants.states import HOME_STATE
from constants.states import START_STATE
from core.keyboards import base_keyboard
from core.keyboards import yes_or_no_without_back_key
from utils.decorators import send_action


logger = getLogger(__name__)


@send_action(ChatAction.TYPING)
async def rule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: Adding parent/child or show data."""
    await management.increment(update, context)
    # pylint: disable=unused-argument
    chat = update.effective_chat
    first_name = update.effective_user.first_name
    if chat.id in context.bot_data.get("user_ids", set()):
        await update.message.reply_text(
            WELCOME_MESSAGE_BACK.format(first_name=first_name),
            reply_markup=base_keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )
        return HOME_STATE

    logger.info("%s started a private chat with the bot", first_name)
    context.bot_data.setdefault("user_ids", set()).add(chat.id)
    await context.bot.send_message(chat_id=update.message.chat_id, text="⚠️")
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=RULE_MESSAGE.format(rule_message=PRIVACY_MESSAGE,
                                 first_name=first_name),
        reply_markup=yes_or_no_without_back_key,
    )
    return START_STATE


@send_action(ChatAction.TYPING)
async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await management.increment(update, context)
    await update.effective_message.reply_text(
        f"Successful rebooted\n\nUse /start to start the chat again"
    )
    return ConversationHandler.END
