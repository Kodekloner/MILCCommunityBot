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
from constants.keys import SETUP_POINTS_KEY
from constants.keys import SET_POINTS_KEY
from constants.keys import CHANGE_POINTS_KEY
from constants.keys import START_COMPETITION_KEY
from constants.keys import STOP_COMPETITION_KEY
from constants.keys import LEADERBOARD_KEY
from constants.keys import SET_TIME_LEADERBOARD_KEY
from constants.keys import DISPLAY_BOARD_KEY
from constants.keys import HIDE_BOARD_KEY
from constants.keys import PARTICIPANT_KEY
from constants.keys import VIEW_PARTICIPANT_KEY
from constants.keys import BAN_PARTICIPANT_KEY
from constants.keys import DISTRIBUTE_TOKEN_KEY
from constants.keys import SET_PRIZE_KEY
from constants.keys import CHANGE_PRIZE_KEY
from constants.keys import SEND_TOKEN_KEY
from constants.keys import ADMIN_CREAT_WALLET_KEY
from constants.keys import VIEW_WALLET_KEY
from constants.keys import DELETE_WALLET_KEY
from constants.keys import ADD_ADDRESS_KEY
from constants.keys import ADD_TWITTER_USER_KEY
from constants.keys import SHOW_ADDRESS_KEY
from constants.keys import SHOW_TWITTER_USER_KEY
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
from constants.states import DELETE_WALLET_STATE
from constants.states import PARTICIPANT_STATE
from constants.states import BAN_PARTICIPANT_STATE
from constants.states import COMFIRM_BAN_PARTICIPANT_STATE
from constants.states import START_STATE
from constants.states import ADMIN_WALLET_STATE
from constants.states import USER_WALLET_STATE
from constants.states import ADD_USER_WALLET_STATE
from constants.states import VIEW_USER_WALLET_STATE
from constants.states import CHANGE_USER_WALLET_STATE
from constants.states import STORE_ADDRESS_STATE
from constants.states import STORE_USERNAME_STATE
from constants.states import ADD_USERNAME_VIEW_ADDR_STATE
from constants.states import VIEW_USERNAME_ADD_ADDR_STATE
from constants.states import CHANGE_USERNAME_STATE
from constants.states import CHANGE_ADDRESS_STATE
from constants.states import OPT_CHANGE_USERNAME_STATE
from constants.states import OPT_CHANGE_ADDRESS_STATE

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
                               wallet.help),
                MessageHandler(filters.Regex(f"^{USER_WALLET_KEY}$"),
                               wallet.wallet),
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("start", start.start),
            ],
            ADD_USER_WALLET_STATE: [
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
            ],
            VIEW_USER_WALLET_STATE: [
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            ADD_USERNAME_VIEW_ADDR_STATE: [
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            VIEW_USERNAME_ADD_ADDR_STATE: [
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            STORE_ADDRESS_STATE: [MessageHandler(filters.TEXT, wallet.store_address)],
            STORE_USERNAME_STATE: [MessageHandler(filters.TEXT, wallet.store_username)],
            OPT_CHANGE_ADDRESS_STATE: [MessageHandler(filters.TEXT, wallet.opt_change_address)],
            OPT_CHANGE_USERNAME_STATE: [MessageHandler(filters.TEXT, wallet.opt_change_username)],
            CHANGE_ADDRESS_STATE: [MessageHandler(filters.TEXT, wallet.store_change_address)],
            CHANGE_USERNAME_STATE: [MessageHandler(filters.TEXT, wallet.store_change_username)],
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
                MessageHandler(filters.Regex(f"^{SETUP_POINTS_KEY}$"),
                               admin.setup_points),
                MessageHandler(filters.Regex(f"^{START_COMPETITION_KEY}$"),
                               admin.star_comp),
                MessageHandler(filters.Regex(f"^{STOP_COMPETITION_KEY}$"),
                               admin.stop_comp),
                MessageHandler(filters.Regex(f"^{LEADERBOARD_KEY}$"),
                               admin.comp_leaderboard),
                MessageHandler(filters.Regex(f"^{PARTICIPANT_KEY}$"),
                               admin.comp_participant),
                MessageHandler(
                    filters.Regex(f"^{DISTRIBUTE_TOKEN_KEY}$"),
                    admin.dis_token,
                ),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_admin,
                ),
            ],
            SETUP_POINTS_STATE: [
                MessageHandler(filters.Regex(f"^{SET_POINTS_KEY}$"),
                               admin.set_point),
                MessageHandler(filters.Regex(f"^{CHANGE_POINTS_KEY}$"),
                               admin.change_points),
                MessageHandler(filters.Regex(f"^{BACK_KEY}$"),
                                admin.back_to_competition),
            ],
            INSERT_POINT_STATE: [MessageHandler(filters.TEXT, admin.insertpoint)],
            UPDATE_POINT_STATE: [MessageHandler(filters.TEXT, admin.updatepoint)],
            LEADERBOARD_SETTING_STATE: [
                MessageHandler(filters.Regex(f"^{SET_TIME_LEADERBOARD_KEY}$"),
                               admin.leaderboard_time_settings),
                MessageHandler(filters.Regex(f"^{DISPLAY_BOARD_KEY}$"),
                              admin.display_leaderboard),
                MessageHandler(filters.Regex(f"^{HIDE_BOARD_KEY}$"),
                               admin.hide_leaderboard),
                MessageHandler(filters.Regex(f"^{BACK_KEY}$"),
                                admin.back_to_competition),
            ],
            TIME_INTERVAL_STATE: [MessageHandler(filters.TEXT, admin.set_time_interval)],
            STORE_DISPLAY_BOARD_STATE: [MessageHandler(filters.TEXT, admin.store_time_interval)],
            SETUP_PRIZE_STATE: [
                MessageHandler(filters.Regex(f"^{SET_PRIZE_KEY}$"),
                               admin.set_prize),
                MessageHandler(filters.Regex(f"^{CHANGE_PRIZE_KEY}$"),
                               admin.change_prize),
                MessageHandler(filters.Regex(f"^{SEND_TOKEN_KEY}$"),
                               admin.send_token),
                MessageHandler(filters.Regex(f"^{BACK_KEY}$"),
                                admin.back_to_competition),
            ],
            INSERT_PRIZE_STATE: [MessageHandler(filters.TEXT, admin.insertprize)],
            UPDATE_PRIZE_STATE: [MessageHandler(filters.TEXT, admin.updateprize)],
            PARTICIPANT_STATE: [
                MessageHandler(filters.Regex(f"^{VIEW_PARTICIPANT_KEY}$"),
                               admin.view_participant),
                MessageHandler(filters.Regex(f"^{BAN_PARTICIPANT_KEY}$"),
                               admin.ban_participant),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_competition,
                ),
            ],
            BAN_PARTICIPANT_STATE: [MessageHandler(filters.TEXT, admin.comfirm_ban_participant)],
            COMFIRM_BAN_PARTICIPANT_STATE: [MessageHandler(filters.TEXT, admin.delete_participant)],
            ADMIN_WALLET_STATE: [
                MessageHandler(filters.Regex(f"^{ADMIN_CREAT_WALLET_KEY}$"),
                               admin.create_wallet),
                MessageHandler(filters.Regex(f"^{VIEW_WALLET_KEY}$"),
                               admin.view_wallet),
                MessageHandler(filters.Regex(f"^{DELETE_WALLET_KEY}$"),
                               admin.delete_wallet),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_admin,
                ),
            ],
            DELETE_WALLET_STATE: [MessageHandler(filters.TEXT, admin.comfirm_delete_wallet)],
            ADD_ADMIN_STATE: [MessageHandler(filters.TEXT, admin.add_admin_to_env)],
        },
        fallbacks=[
            MessageHandler(filters.ALL, admin.handle_invalid_message)
        ],
        name="base_conversation_handler",
        persistent=True,
    )
    return conversation_handler
