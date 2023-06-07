from telegram import ReplyKeyboardMarkup

from constants import EMAIL
from constants import NO
from constants import PHONE
from constants import YES
from constants.keys import BACK_KEY, FEEDBACK_KEY
from constants.keys import BACK_TO_HOME_KEY
from constants.keys import HELP_KEY
from constants.keys import USER_WALLET_KEY
from constants.keys import ADMIN_KEY
from constants.keys import TWITTER_KEY
from constants.keys import SEARCH_KEY
from constants.keys import DATE_KEY
from constants.keys import SEND_TWEETS_KEY
from constants.keys import STOP_SENDIND_TWEETS_KEY
from constants.keys import COMPETITION_KEY
from constants.keys import ADMIN_WALLET_KEY
from constants.keys import START_COMPETITION_KEY
from constants.keys import STOP_COMPETITION_KEY
from constants.keys import DISTRIBUTE_TOKEN_KEY
from constants.keys import ADMIN_CREAT_WALLET_KEY
from constants.keys import VIEW_WALLET_KEY
from constants.keys import ADD_ADDRESS_KEY
from constants.keys import ADD_TWITTER_USER_KEY
from constants.keys import SHOW_ADDRESS_KEY
from constants.keys import SHOW_TWITTER_USER_KEY
from constants.keys import CHANGE_ADDRESS_KEY
from constants.keys import CHANGE_TWITTER_USER_KEY



base_reply_keyboard: list = [
    [HELP_KEY, USER_WALLET_KEY]
]
base_keyboard = ReplyKeyboardMarkup(base_reply_keyboard, resize_keyboard=True)

back_reply_keyboard = [[BACK_KEY]]
back_keyboard = ReplyKeyboardMarkup(back_reply_keyboard, resize_keyboard=True)

yes_or_no_reply_keyboard = [[NO, YES], [BACK_KEY]]
yes_or_no_keyboard = ReplyKeyboardMarkup(yes_or_no_reply_keyboard,
                                         resize_keyboard=True)

yes_or_no_without_back_key_reply_keyboard = [
    [NO, YES],
]
yes_or_no_without_back_key = ReplyKeyboardMarkup(
    yes_or_no_without_back_key_reply_keyboard, resize_keyboard=True)

email_or_phone_reply_keyboard = [[EMAIL], [PHONE]]
email_or_phone_keyboard = ReplyKeyboardMarkup(email_or_phone_reply_keyboard,
                                              resize_keyboard=True)

admin_reply_keyboard = [
    [TWITTER_KEY, COMPETITION_KEY, ADMIN_WALLET_KEY],
    [BACK_TO_HOME_KEY],
]
admin_keyboard = ReplyKeyboardMarkup(admin_reply_keyboard,
                                     resize_keyboard=True)

twitter_reply_keyboard = [
    [SEARCH_KEY, DATE_KEY],
    [SEND_TWEETS_KEY, STOP_SENDIND_TWEETS_KEY],
    [BACK_KEY],
]
twitter_keyboard = ReplyKeyboardMarkup(twitter_reply_keyboard,
                                       resize_keyboard=True)

competition_reply_keyboard = [
    [START_COMPETITION_KEY, STOP_COMPETITION_KEY, DISTRIBUTE_TOKEN_KEY],
    [BACK_KEY],
]
competition_keyboard = ReplyKeyboardMarkup(competition_reply_keyboard,
                                            resize_keyboard=True)

admin_wallet_reply_keyboard = [
    [ADMIN_CREAT_WALLET_KEY, VIEW_WALLET_KEY],
    [BACK_KEY],
]
admin_wallet_keyboard = ReplyKeyboardMarkup(admin_wallet_reply_keyboard,
                                            resize_keyboard=True)

add_user_wallet_reply_keyboard = [
    [ADD_ADDRESS_KEY, ADD_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
add_user_wallet_keyboard = ReplyKeyboardMarkup(add_user_wallet_reply_keyboard,
                                            resize_keyboard=True)

view_user_add_addr_reply_keyboard = [
    [ADD_ADDRESS_KEY, SHOW_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
view_user_add_addr_keyboard = ReplyKeyboardMarkup(view_user_add_addr_reply_keyboard,
                                            resize_keyboard=True)

change_add_reply_keyboard = [
    [CHANGE_ADDRESS_KEY],
    [BACK_KEY],
]
change_add_keyboard = ReplyKeyboardMarkup(change_add_reply_keyboard,
                                            resize_keyboard=True)

change_username_reply_keyboard = [
    [CHANGE_TWITTER_USER_KEY],
    [BACK_KEY],
]
change_username_keyboard = ReplyKeyboardMarkup(change_username_reply_keyboard,
                                            resize_keyboard=True)

view_user_wallet_reply_keyboard = [
    [SHOW_ADDRESS_KEY, SHOW_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
view_user_wallet_keyboard = ReplyKeyboardMarkup(view_user_wallet_reply_keyboard,
                                            resize_keyboard=True)

add_user_view_addr_reply_keyboard = [
    [SHOW_ADDRESS_KEY, ADD_TWITTER_USER_KEY],
    [BACK_TO_HOME_KEY],
]
add_user_view_addr_keyboard = ReplyKeyboardMarkup(add_user_view_addr_reply_keyboard,
                                            resize_keyboard=True)
