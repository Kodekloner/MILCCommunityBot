from logging import getLogger

from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import filters
from telegram.ext import MessageHandler

from commands import admin
from commands import privacy
from commands import rule
from commands import start
from commands import wallet
from constants.keys import BACK_KEY
from constants.keys import BACK_TO_HOME_KEY
from constants.keys import HELP_KEY
from constants.keys import TWITTER_KEY
from constants.keys import ADMIN_WALLET_KEY
from constants.keys import COMPETITION_KEY
from constants.keys import USER_WALLET_KEY
from constants.keys import SEARCH_KEY
from constants.keys import DATE_KEY
from constants.keys import SEND_TWEETS_KEY
from constants.keys import STOP_SENDIND_TWEETS_KEY
from constants.keys import START_COMPETITION_KEY
from constants.keys import STOP_COMPETITION_KEY
from constants.keys import DISTRIBUTE_TOKEN_KEY
from constants.keys import ADMIN_CREAT_WALLET_KEY
from constants.keys import VIEW_WALLET_KEY
from constants.keys import ADD_ADDRESS_KEY
from constants.keys import ADD_TWITTER_USER_KEY
from constants.keys import ADD_TWITTER_PASS_KEY
from constants.keys import SHOW_ADDRESS_KEY
from constants.keys import SHOW_TWITTER_USER_KEY
from constants.keys import SHOW_TWITTER_PASS_KEY
from constants.states import ADMIN_STATE
from constants.states import HOME_STATE
from constants.states import TWITTER_STATE
from constants.states import SEARCH_STATE
from constants.states import SEARCH_DATE_STATE
from constants.states import COMPETITION_STATE
from constants.states import START_STATE
from constants.states import ADMIN_WALLET_STATE
from constants.states import USER_WALLET_STATE
from constants.states import ADD_USER_WALLET_STATE
from constants.states import VIEW_USER_WALLET_STATE
from constants.states import CHANGE_USER_WALLET_STATE
from constants.states import STORE_ADDRESS_STATE
from constants.states import STORE_USERNAME_STATE
from constants.states import STORE_PASS_STATE

# Init logger

logger = getLogger(__name__)

def base_conversation_handler():
    """Process a /start command."""
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", rule.rule)],
        states={
            # start ==>
            START_STATE: [MessageHandler(filters.TEXT, start.start)],
            # home ==>
            HOME_STATE: [
                MessageHandler(filters.Regex(f"^{HELP_KEY}$"),
                               admin.admin),
                MessageHandler(filters.Regex(f"^{USER_WALLET_KEY}$"),
                               wallet.wallet),
                CommandHandler("admin", admin.admin),
                CommandHandler("start", start.start),
                CommandHandler("privacy", privacy.privacy),
            ],
            ADD_USER_WALLET_STATE: [
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_PASS_KEY}$"),
                               wallet.add_pass),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            VIEW_USER_WALLET_STATE: [
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_PASS_KEY}$"),
                               wallet.view_pass),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            STORE_ADDRESS_STATE: [MessageHandler(filters.TEXT, wallet.store_address)],
            STORE_USERNAME_STATE: [MessageHandler(filters.TEXT, wallet.store_username)],
            STORE_PASS_STATE: [MessageHandler(filters.TEXT, wallet.store_pass)],
            ADMIN_STATE: [
                MessageHandler(filters.Regex(f"^{COMPETITION_KEY}$"),
                               admin.competition),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               admin.back_to_home),
                MessageHandler(
                    filters.Regex(f"^{ADMIN_WALLET_KEY}$"),
                    admin.admin_wallet,
                ),
                MessageHandler(
                    filters.Regex(f"^{TWITTER_KEY}$"),
                    admin.twitter,
                ),
            ],
            TWITTER_STATE: [
                MessageHandler(filters.Regex(f"^{SEARCH_KEY}$"),
                               admin.search),
                MessageHandler(filters.Regex(f"^{DATE_KEY}$"),
                               admin.add_date),
                MessageHandler(
                    filters.Regex(f"^{SEND_TWEETS_KEY}$"),
                    admin.admin_send_tweets,
                ),
                MessageHandler(
                    filters.Regex(f"^{STOP_SENDIND_TWEETS_KEY}$"),
                    admin.stop_tweets,
                ),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_admin,
                ),
            ],
            SEARCH_STATE: [MessageHandler(filters.TEXT, admin.store_search)],
            SEARCH_DATE_STATE: [MessageHandler(filters.TEXT, admin.store_date)],
            COMPETITION_STATE: [
                MessageHandler(filters.Regex(f"^{START_COMPETITION_KEY}$"),
                               admin.star_comp),
                MessageHandler(filters.Regex(f"^{STOP_COMPETITION_KEY}$"),
                               admin.stop_comp),
                MessageHandler(
                    filters.Regex(f"^{DISTRIBUTE_TOKEN_KEY}$"),
                    admin.dis_token,
                ),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_admin,
                ),
            ],
            ADMIN_WALLET_STATE: [
                MessageHandler(filters.Regex(f"^{ADMIN_CREAT_WALLET_KEY}$"),
                               admin.create_wallet),
                MessageHandler(filters.Regex(f"^{VIEW_WALLET_KEY}$"),
                               admin.view_wallet),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_admin,
                ),
            ],
        },
        fallbacks=[],
        name="base_conversation_handler",
        # persistent=False,
    )
    return conversation_handler
