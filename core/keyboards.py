from telegram import ReplyKeyboardMarkup

from constants import EMAIL
from constants import NO
from constants import PHONE
from constants import YES
from constants.keys import BACK_KEY, FEEDBACK_KEY
from constants.keys import BACK_TO_HOME_KEY
from constants.keys import HELP_KEY
from constants.keys import USER_WALLET_KEY
from constants.keys import SELECT_GROUP_KEY
from constants.keys import ADMIN_KEY
from constants.keys import TWITTER_KEY
from constants.keys import SEARCH_KEY
from constants.keys import DATE_KEY
from constants.keys import GET_TWEETS_KEY
from constants.keys import SEND_TWEETS_KEY
from constants.keys import PROCEED_KEY
from constants.keys import STOP_GET_TWEETS_KEY
from constants.keys import STOP_SEND_TWEETS_KEY
from constants.keys import STOP_SENDIND_TWEETS_KEY
from constants.keys import UPLOAD_PHOTO_KEY
from constants.keys import COMPETITION_KEY
from constants.keys import ADMIN_WALLET_KEY
from constants.keys import SETUP_POINTS_KEY
from constants.keys import SET_POINTS_KEY
from constants.keys import CHANGE_POINTS_KEY
from constants.keys import LEADERBOARD_KEY
from constants.keys import SET_TIME_LEADERBOARD_KEY
from constants.keys import DISPLAY_BOARD_KEY
from constants.keys import HIDE_BOARD_KEY
from constants.keys import SECS_KEY
from constants.keys import MINS_KEY
from constants.keys import HOURS_KEY
from constants.keys import DAYS_KEY
from constants.keys import PARTICIPANT_KEY
from constants.keys import VIEW_PARTICIPANT_KEY
from constants.keys import BAN_PARTICIPANT_KEY
from constants.keys import START_COMPETITION_KEY
from constants.keys import STOP_COMPETITION_KEY
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
from constants.keys import CHANGE_ADDRESS_KEY
from constants.keys import CHANGE_TWITTER_USER_KEY


base_reply_keyboard: list = [
    [HELP_KEY, USER_WALLET_KEY]
]
base_keyboard = ReplyKeyboardMarkup(base_reply_keyboard, resize_keyboard=True, selective=True)

back_reply_keyboard = [[BACK_KEY]]
back_keyboard = ReplyKeyboardMarkup(back_reply_keyboard, resize_keyboard=True, selective=True)

yes_or_no_reply_keyboard = [[NO, YES], [BACK_KEY]]
yes_or_no_keyboard = ReplyKeyboardMarkup(yes_or_no_reply_keyboard,
                                         resize_keyboard=True, selective=True)

yes_or_no_without_back_key_reply_keyboard = [
    [NO, YES],
]
yes_or_no_without_back_key = ReplyKeyboardMarkup(
    yes_or_no_without_back_key_reply_keyboard, resize_keyboard=True, selective=True)

email_or_phone_reply_keyboard = [[EMAIL], [PHONE]]
email_or_phone_keyboard = ReplyKeyboardMarkup(email_or_phone_reply_keyboard,
                                              resize_keyboard=True, selective=True)

back_to_home_reply_keyboard = [
    [BACK_TO_HOME_KEY],
]
back_to_home_keyboard = ReplyKeyboardMarkup(back_to_home_reply_keyboard,
                                     resize_keyboard=True, selective=True)

admin_reply_keyboard = [
    [TWITTER_KEY, COMPETITION_KEY, ADMIN_WALLET_KEY],
    [BACK_TO_HOME_KEY],
]
admin_keyboard = ReplyKeyboardMarkup(admin_reply_keyboard,
                                     resize_keyboard=True, selective=True)

twitter_reply_keyboard = [
    [SEARCH_KEY, UPLOAD_PHOTO_KEY],
    [SEND_TWEETS_KEY, STOP_SENDIND_TWEETS_KEY],
    [BACK_KEY],
]
twitter_keyboard = ReplyKeyboardMarkup(twitter_reply_keyboard,
                                       resize_keyboard=True, selective=True)

get_send_tweets_reply_keyboard = [
    [GET_TWEETS_KEY, SEND_TWEETS_KEY],
    [BACK_KEY],
]
get_send_tweets_keyboard = ReplyKeyboardMarkup(get_send_tweets_reply_keyboard,
                                       resize_keyboard=True, selective=True)

stop_get_send_tweets_reply_keyboard = [
    [STOP_GET_TWEETS_KEY, STOP_SEND_TWEETS_KEY],
    [BACK_KEY],
]
stop_get_send_tweets_keyboard = ReplyKeyboardMarkup(stop_get_send_tweets_reply_keyboard,
                                       resize_keyboard=True, selective=True)

select_group_reply_keyboard = [
    [PROCEED_KEY],
    [BACK_KEY],
]
select_group_keyboard = ReplyKeyboardMarkup(select_group_reply_keyboard,
                                       resize_keyboard=True, selective=True)

send_tweets_reply_keyboard = [
    [SEND_TWEETS_KEY],
    [BACK_KEY],
]
send_tweets_keyboard = ReplyKeyboardMarkup(send_tweets_reply_keyboard,
                                       resize_keyboard=True, selective=True)

stop_send_tweets_reply_keyboard = [
    [STOP_SEND_TWEETS_KEY],
    [BACK_KEY],
]
stop_send_tweets_keyboard = ReplyKeyboardMarkup(stop_send_tweets_reply_keyboard,
                                       resize_keyboard=True, selective=True)

competition_reply_keyboard = [
    [SETUP_POINTS_KEY, START_COMPETITION_KEY, STOP_COMPETITION_KEY],
    [LEADERBOARD_KEY, DISTRIBUTE_TOKEN_KEY, PARTICIPANT_KEY],
    [BACK_KEY],
]
competition_keyboard = ReplyKeyboardMarkup(competition_reply_keyboard,
                                            resize_keyboard=True, selective=True)

setup_points_reply_keyboard = [
    [SET_POINTS_KEY, CHANGE_POINTS_KEY],
    [BACK_KEY],
]
setup_points_keyboard = ReplyKeyboardMarkup(setup_points_reply_keyboard,
                                            resize_keyboard=True, selective=True)

setup_prize_reply_keyboard = [
    [SET_PRIZE_KEY, CHANGE_PRIZE_KEY, SEND_TOKEN_KEY],
    [BACK_KEY],
]
setup_prize_keyboard = ReplyKeyboardMarkup(setup_prize_reply_keyboard,
                                            resize_keyboard=True, selective=True)

leaderboard_setting_reply_keyboard = [
    [SET_TIME_LEADERBOARD_KEY, DISPLAY_BOARD_KEY, HIDE_BOARD_KEY],
    [BACK_KEY],
]
leaderboard_setting_keyboard = ReplyKeyboardMarkup(leaderboard_setting_reply_keyboard,
                                            resize_keyboard=True, selective=True)

display_leaderboard_reply_keyboard = [
    [DISPLAY_BOARD_KEY],
    [BACK_KEY],
]
display_leaderboard_keyboard = ReplyKeyboardMarkup(display_leaderboard_reply_keyboard,
                                            resize_keyboard=True, selective=True)

hide_leaderboard_reply_keyboard = [
    [HIDE_BOARD_KEY],
    [BACK_KEY],
]
hide_leaderboard_keyboard = ReplyKeyboardMarkup(hide_leaderboard_reply_keyboard,
                                            resize_keyboard=True, selective=True)

dis_token_reply_keyboard = [
    [SEND_TOKEN_KEY],
    [BACK_KEY],
]
dis_token_keyboard = ReplyKeyboardMarkup(dis_token_reply_keyboard,
                                            resize_keyboard=True, selective=True)

leaderboard_time_settings_reply_keyboard = [
    [SECS_KEY, MINS_KEY],
    [HOURS_KEY, DAYS_KEY],
    [BACK_KEY],
]
leaderboard_time_settings_keyboard = ReplyKeyboardMarkup(leaderboard_time_settings_reply_keyboard,
                                            resize_keyboard=True, selective=True)

participant_reply_keyboard = [
    [VIEW_PARTICIPANT_KEY, BAN_PARTICIPANT_KEY],
    [BACK_KEY],
]
participant_keyboard = ReplyKeyboardMarkup(participant_reply_keyboard,
                                            resize_keyboard=True, selective=True)

admin_wallet_reply_keyboard = [
    [ADMIN_CREAT_WALLET_KEY, VIEW_WALLET_KEY, DELETE_WALLET_KEY],
    [BACK_KEY],
]
admin_wallet_keyboard = ReplyKeyboardMarkup(admin_wallet_reply_keyboard,
                                            resize_keyboard=True, selective=True)

add_user_wallet_reply_keyboard = [
    [ADD_ADDRESS_KEY, ADD_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
add_user_wallet_keyboard = ReplyKeyboardMarkup(add_user_wallet_reply_keyboard,
                                            resize_keyboard=True, selective=True)

add_user_wallet_group_reply_keyboard = [
    [ADD_ADDRESS_KEY, ADD_TWITTER_USER_KEY, SELECT_GROUP_KEY],
    [BACK_TO_HOME_KEY],
]
add_user_wallet_group_keyboard = ReplyKeyboardMarkup(add_user_wallet_group_reply_keyboard,
                                            resize_keyboard=True, selective=True)

view_user_add_addr_reply_keyboard = [
    [ADD_ADDRESS_KEY, SHOW_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
view_user_add_addr_keyboard = ReplyKeyboardMarkup(view_user_add_addr_reply_keyboard,
                                            resize_keyboard=True, selective=True)

view_user_add_addr_group_reply_keyboard = [
    [ADD_ADDRESS_KEY, SHOW_TWITTER_USER_KEY, SELECT_GROUP_KEY],
    [BACK_TO_HOME_KEY],
]
view_user_add_addr_group_keyboard = ReplyKeyboardMarkup(view_user_add_addr_group_reply_keyboard,
                                            resize_keyboard=True, selective=True)

change_add_reply_keyboard = [
    [CHANGE_ADDRESS_KEY],
    [BACK_KEY],
]
change_add_keyboard = ReplyKeyboardMarkup(change_add_reply_keyboard,
                                            resize_keyboard=True, selective=True)

change_username_reply_keyboard = [
    [CHANGE_TWITTER_USER_KEY],
    [BACK_KEY],
]
change_username_keyboard = ReplyKeyboardMarkup(change_username_reply_keyboard,
                                            resize_keyboard=True, selective=True)

view_user_wallet_reply_keyboard = [
    [SHOW_ADDRESS_KEY, SHOW_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
view_user_wallet_keyboard = ReplyKeyboardMarkup(view_user_wallet_reply_keyboard,
                                            resize_keyboard=True, selective=True)

view_user_wallet_group_reply_keyboard = [
    [SHOW_ADDRESS_KEY, SHOW_TWITTER_USER_KEY, SELECT_GROUP_KEY],
    [BACK_TO_HOME_KEY],
]
view_user_wallet_group_keyboard = ReplyKeyboardMarkup(view_user_wallet_group_reply_keyboard,
                                            resize_keyboard=True, selective=True)

add_user_view_addr_reply_keyboard = [
    [SHOW_ADDRESS_KEY, ADD_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
add_user_view_addr_keyboard = ReplyKeyboardMarkup(add_user_view_addr_reply_keyboard,
                                            resize_keyboard=True, selective=True)

add_user_view_addr_group_reply_keyboard = [
    [SHOW_ADDRESS_KEY, ADD_TWITTER_USER_KEY, SELECT_GROUP_KEY],
    [BACK_TO_HOME_KEY],
]
add_user_view_addr_group_keyboard = ReplyKeyboardMarkup(add_user_view_addr_group_reply_keyboard,
                                            resize_keyboard=True, selective=True)
