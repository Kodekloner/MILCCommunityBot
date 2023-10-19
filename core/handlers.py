from logging import getLogger

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CallbackQueryHandler,
)

from commands import admin
from commands import rule
from commands import start
from commands import wallet
from constants.keys import BACK_KEY
from constants.keys import BACK_TO_HOME_KEY
from constants.keys import HELP_KEY
from constants.keys import TWITTER_KEY
from constants.keys import LEAVE_COMP_KEY
from constants.keys import ADMIN_WALLET_KEY
from constants.keys import COMPETITION_KEY
from constants.keys import USER_WALLET_KEY
from constants.keys import SELECT_GROUP_KEY
from constants.keys import SEARCH_KEY
from constants.keys import DATE_KEY
from constants.keys import SEND_TWEETS_KEY
from constants.keys import STOP_SENDIND_TWEETS_KEY
from constants.keys import UPLOAD_PHOTO_KEY
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
from constants.states import UPLOAD_PHOTO_STATE
from constants.states import SEARCH_DATE_STATE
from constants.states import GET_SEND_TWEETS_STATE
from constants.states import STOP_GET_SEND_TWEETS_STATE
from constants.states import SELECT_GROUPS_STATE
from constants.states import SELECT_STOP_GROUPS_STATE
from constants.states import SEND_TWEETS_STATE
from constants.states import STOP_SEND_TWEETS_STATE
from constants.states import COMPETITION_STATE
from constants.states import SETUP_POINTS_STATE
from constants.states import INSERT_POINT_STATE
from constants.states import UPDATE_POINT_STATE
from constants.states import LEADERBOARD_SETTING_STATE
from constants.states import SELECT_GROUPS_COMPETITION_STATE
from constants.states import DISPLAY_LEADERBOARD_STATE
from constants.states import SELECT_HIDE_GROUPS_COMPETITION_STATE
from constants.states import HIDE_LEADERBOARD_STATE
from constants.states import TIME_INTERVAL_STATE
from constants.states import STORE_DISPLAY_BOARD_STATE
from constants.states import SETUP_PRIZE_STATE
from constants.states import INSERT_PRIZE_STATE
from constants.states import UPDATE_PRIZE_STATE
from constants.states import SELECT_GROUPS_DIS_STATE
from constants.states import SEND_TOKEN_STATE
from constants.states import DELETE_WALLET_STATE
from constants.states import PARTICIPANT_STATE
from constants.states import BAN_PARTICIPANT_STATE
from constants.states import COMFIRM_BAN_PARTICIPANT_STATE
from constants.states import START_STATE
from constants.states import ADMIN_WALLET_STATE
from constants.states import USER_WALLET_STATE
from constants.states import LEAVE_COMP_STATE
from constants.states import COMFIRM_LEAVE_COMP_STATE
from constants.states import ADD_USER_WALLET_STATE
from constants.states import ADD_USER_WALLET_GROUP_STATE
from constants.states import INSERT_USER_GROUP_STATE
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
from constants.states import VIEW_USER_WALLET_DM_STATE
from constants.states import ADD_USERNAME_VIEW_ADDR_DM_STATE
from constants.states import VIEW_USERNAME_ADD_ADDR_DM_STATE

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
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{HELP_KEY}$"),
                               wallet.help),
                MessageHandler(filters.Regex(f"^{USER_WALLET_KEY}$"),
                               wallet.wallet),
                MessageHandler(filters.Regex(f"^{LEAVE_COMP_KEY}$"),
                               wallet.leave_comp),
            ],
            COMFIRM_LEAVE_COMP_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, wallet.comfirm_leave_comp),
            ],
            ADD_USER_WALLET_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            ADD_USER_WALLET_GROUP_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
                MessageHandler(filters.Regex(f"^{SELECT_GROUP_KEY}$"),
                               wallet.user_select_group),
            ],
            INSERT_USER_GROUP_STATE: [
                CallbackQueryHandler(wallet.button_callback_user_group),
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
                MessageHandler(filters.Regex(f"^{SELECT_GROUP_KEY}$"),
                               wallet.user_select_group),
            ],
            VIEW_USER_WALLET_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            VIEW_USER_WALLET_DM_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{SELECT_GROUP_KEY}$"),
                              wallet.user_select_group),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            ADD_USERNAME_VIEW_ADDR_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            ADD_USERNAME_VIEW_ADDR_DM_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SHOW_ADDRESS_KEY}$"),
                               wallet.view_address),
                MessageHandler(filters.Regex(f"^{ADD_TWITTER_USER_KEY}$"),
                               wallet.add_username),
                MessageHandler(filters.Regex(f"^{SELECT_GROUP_KEY}$"),
                               wallet.user_select_group),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            VIEW_USERNAME_ADD_ADDR_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            VIEW_USERNAME_ADD_ADDR_DM_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{ADD_ADDRESS_KEY}$"),
                               wallet.add_address),
                MessageHandler(filters.Regex(f"^{SHOW_TWITTER_USER_KEY}$"),
                               wallet.view_username),
                MessageHandler(filters.Regex(f"^{SELECT_GROUP_KEY}$"),
                              wallet.user_select_group),
                MessageHandler(filters.Regex(f"^{BACK_TO_HOME_KEY}$"),
                               wallet.back_to_home),
            ],
            STORE_ADDRESS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, wallet.store_address)
            ],
            STORE_USERNAME_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, wallet.store_username)
            ],
            OPT_CHANGE_ADDRESS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, wallet.opt_change_address)
            ],
            OPT_CHANGE_USERNAME_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, wallet.opt_change_username)
            ],
            CHANGE_ADDRESS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, wallet.store_change_address)
            ],
            CHANGE_USERNAME_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, wallet.store_change_username)
            ],
            ADMIN_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
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
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SEARCH_KEY}$"),
                               admin.search),
                MessageHandler(
                    filters.Regex(f"^{SEND_TWEETS_KEY}$"),
                    admin.get_send_tweet,
                ),
                MessageHandler(
                    filters.Regex(f"^{STOP_SENDIND_TWEETS_KEY}$"),
                    admin.stop_get_send_tweet,
                ),
                MessageHandler(
                    filters.Regex(f"^{UPLOAD_PHOTO_KEY}$"),
                    admin.upload_photo,
                ),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_admin,
                ),
            ],
            UPLOAD_PHOTO_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.ALL, admin.store_photo)
            ],
            SEARCH_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.store_search)
            ],
            GET_SEND_TWEETS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.get_tweets_select_group)
            ],
            SELECT_GROUPS_STATE: [
                CallbackQueryHandler(admin.button_callback),
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.get_selected_groups),
            ],
            SEND_TWEETS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.admin_send_tweets)
            ],
            STOP_GET_SEND_TWEETS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.stop_get_tweets_select_group)
            ],
            SELECT_STOP_GROUPS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                CallbackQueryHandler(admin.button_callback_stop),
                MessageHandler(filters.TEXT, admin.get_selected_groups_stop),
            ],
            STOP_SEND_TWEETS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.admin_stop_send_tweets)
            ],
            COMPETITION_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SETUP_POINTS_KEY}$"),
                               admin.setup_points),
                MessageHandler(filters.Regex(f"^{START_COMPETITION_KEY}$"),
                               admin.star_comp),
                MessageHandler(filters.Regex(f"^{STOP_COMPETITION_KEY}$"),
                               admin.stop_comp),
                MessageHandler(filters.Regex(f"^{LEADERBOARD_KEY}$"),
                               admin.comp_leaderboard),
                MessageHandler(filters.Regex(f"^Participant\(s\) 👨‍💼$"),
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
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SET_POINTS_KEY}$"),
                               admin.set_point),
                MessageHandler(filters.Regex(f"^{CHANGE_POINTS_KEY}$"),
                               admin.change_points),
                MessageHandler(filters.Regex(f"^{BACK_KEY}$"),
                                admin.back_to_competition),
            ],
            INSERT_POINT_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.insertpoint)
            ],
            UPDATE_POINT_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.updatepoint)
            ],
            LEADERBOARD_SETTING_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SET_TIME_LEADERBOARD_KEY}$"),
                               admin.leaderboard_time_settings),
                MessageHandler(filters.Regex(f"^{DISPLAY_BOARD_KEY}$"),
                              admin.get_groups_display_leaderboard),
                MessageHandler(filters.Regex(f"^{HIDE_BOARD_KEY}$"),
                               admin.get_groups_hide_leaderboard),
                MessageHandler(filters.Regex(f"^{BACK_KEY}$"),
                                admin.back_to_competition),
            ],
            SELECT_GROUPS_COMPETITION_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                CallbackQueryHandler(admin.button_callback_com),
                MessageHandler(filters.TEXT, admin.get_selected_groups_com),
            ],
            DISPLAY_LEADERBOARD_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.display_leaderboard)
            ],
            SELECT_HIDE_GROUPS_COMPETITION_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                CallbackQueryHandler(admin.button_callback_hide),
                MessageHandler(filters.TEXT, admin.get_selected_hide_groups_com),
            ],
            HIDE_LEADERBOARD_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.hide_leaderboard)
            ],
            TIME_INTERVAL_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.set_time_interval)
            ],
            STORE_DISPLAY_BOARD_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.store_time_interval)
            ],
            SETUP_PRIZE_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^{SET_PRIZE_KEY}$"),
                               admin.set_prize),
                MessageHandler(filters.Regex(f"^{CHANGE_PRIZE_KEY}$"),
                               admin.change_prize),
                MessageHandler(filters.Regex(f"^{SEND_TOKEN_KEY}$"),
                               admin.get_groups_token),
                MessageHandler(filters.Regex(f"^{BACK_KEY}$"),
                                admin.back_to_competition),
            ],
            INSERT_PRIZE_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.insertprize)
            ],
            UPDATE_PRIZE_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.updateprize)
            ],
            SELECT_GROUPS_DIS_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                CallbackQueryHandler(admin.button_callback_dis),
                MessageHandler(filters.TEXT, admin.get_selected_groups_dis),
            ],
            SEND_TOKEN_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.send_token)
            ],
            PARTICIPANT_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.Regex(f"^View Participant\(s\)$"),
                               admin.view_participant),
                MessageHandler(filters.Regex(f"^Ban Participant\(s\)$"),
                               admin.ban_participant),
                MessageHandler(
                    filters.Regex(f"^{BACK_KEY}$"),
                    admin.back_to_competition,
                ),
            ],
            BAN_PARTICIPANT_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.comfirm_ban_participant)
            ],
            COMFIRM_BAN_PARTICIPANT_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.delete_participant)
            ],
            ADMIN_WALLET_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
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
            DELETE_WALLET_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.comfirm_delete_wallet)
            ],
            ADD_ADMIN_STATE: [
                CommandHandler("admin", admin.admin),
                CommandHandler("addadmin", admin.add_admin),
                CommandHandler("groups", admin.get_groups),
                CommandHandler("reboot", rule.reboot),
                CommandHandler("reset", admin.reset),
                MessageHandler(filters.TEXT, admin.add_admin_to_env)],
        },
        fallbacks=[
            MessageHandler(filters.ALL, admin.handle_invalid_message)
        ],
        name="base_conversation_handler",
        persistent=True,
    )
    return conversation_handler
