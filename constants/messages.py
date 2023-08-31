SET_POINT_SYSTEM_WITH_POINTS: str = (
    "Each *Tweet* is {tweet} point(s).\n"
    "Each *replies* is {reply} point(s).\n"
    "Each *likes* is {like} point(s).\n"
    "Each *retweet* is {retweet} point(s).\n"
    "Each *quote* is {quote} point(s).\n"
    "\n"
    "To change the point tap on the Change points 📝"
)

SET_POINT_SYSTEM: str = (
    "To set point for the competition tap on the Set points"
)

SET_PRIZE_SYSTEM: str = (
    "To set prize for the competition tap on the Set prize"
)

MESSAGE_FOR_SET_POINT: str = (
    "Please set the competition point in the following format: \n"
    "\n"
    "tweets-1\n"
    "replies-1\n"
    "likes-1\n"
    "retweets-1\n"
    "quotes-1\n"
    "\n"
)

MESSAGE_FOR_SET_PRIZE: str = (
    "Please set the competition prize in the following format: \n"
    "\n"
    "5.002\n"
    "4\n"
    "3.005\n"
    "2.006\n"
    "1.08\n"
    "\n"
    "Note:\n"
    "these prize could be any value but the first on the top will be for the first position,\n"
    "the second on the list will be for the second postion, in that order."
)

MESSAGE_FOR_CHANGE_PRIZE: str = (
    "Please set the competition prize in the following format: \n"
    "positions-prizes\n"
    "Example:"
    "\n"
    "1-5.002\n"
    "4-4\n"
    "\n"
    "Note:\n"
    "these prize could be any value but the first number is the position,\n"
    "the number after the '-' is the second prize."
)

MESSAGE_FOR_CHANGE_POINT: str = (
    "Please change the competition point in the following format: \n"
    "\n"
    "tweets-1\n"
    "replies-1\n"
    "likes-1\n"
    "retweets-1\n"
    "quotes-1\n"
    "\n"
)

MESSAGE_FOR_WRONG_SET_POINT: str = (
    "You already set the points to,\n"
    "tap on Change points 📝, to change the points"
)

MESSAGE_FOR_WRONG_SET_PRIZE: str = (
    "You already set the prize,\n"
    "tap on Change points 📝, to change the points"
)

MESSAGE_FOR_WRONG_CHANGE_PRIZE: str = (
    "You haven't set the prize yet, plase do so first,\n"
)

MESSAGE_FOR_GET_LOGIN_DATA: str = (
    "Please send me login information in the following format and format: \n"
    "\n"
    "username\n"
    "password\n"
    "\n"
    "*we don,t save your username and Password* \n"
    "Next step if you want to save the session on our servers\n"
    "\n"
    "*what is session ?* \n"
    "when you use your mobile device, you login to Instagram once and then you "
    "can use it for a long time without logging in again. This is because "
    "Instagram stores your session on your device and you can use it to "
    "login to Instagram without entering your username and password again.\n"
    "\n"
    "{instagram_assistant_id}")
WHAT_DO_YOU_WANT: str = "what do you want ?"
YOU_WERE_ALREADY_LOGGED_IN: str = "You Were Already Logged In"
LOGGED_IN_SUCCESSFULLY: str = "Logged In Successfully"
DOWNLOAD_COMPLETED: str = "Download Complete"
LINK_IS_INVALID: str = "Link is Invalid, check your Link and Try Again"
STARTING_DOWNLOAD: str = "Starting Download ..."
UPLOAD_IN_TELEGRAM: str = "Upload In Telegram ..."
IS_VIDEO: str = "video"
WELCOME_MESSAGE: str = (
    "Hello {first_name}, welcome to MILC Community Bot.\n"
    "\n"
    "**Before we start, what can the Bot actually do?**\n"
    "\n"
    "MILC Community Bot allows you to earn rewards by promoting and spreading the word about the MILC project on Twitter. To make this work, the Bot has a Competition function and integrated Reward Distributions.\n"
    "\n"
    "**What's the point of it?**\n"
    "\n"
    "With your help and the incentives that come with it, we want to increase the visibility and reach of the MILC project.\n"
    "\n"
    "\n"
    "Let's go to the moon together! 🚀🌕")

WELCOME_MESSAGE_BACK: str = (
    "Hello {first_name}, welcome back to MILC Community Bot.\n"
    "\n"
    "Let's go to the moon together! 🚀🌕")


SEND_ME_THE_MEDIA_YOU_WANT_TO_UPLOAD_ON_INSTAGRAM: str = (
    "Send me the media you want to upload on Instagram")
SEND_ME_THE_CAPTION_OF_POST_YOU_WANT_TO_UPLOAD_ON_INSTAGRAM: str = (
    "Send me the caption of post you want to upload on Instagram")
SEND_ME_THE_TITLE_OF_POST_YOU_WANT_TO_UPLOAD_ON_INSTAGRAM: str = (
    "Send me the title of IGTV you want to upload on Instagram")
WHAT_TYPE_OF_CONTENT_DO_YOU_WANT_TO_UPLOAD_ON_INSTAGRAM: str = (
    f"{LOGGED_IN_SUCCESSFULLY} What type of content do you want to upload on Instagram"
)
ARE_YOU_SURE_OF_UPLOADING_THIS_MEDIA: str = "Are you sure of uploading this media?"
MEDIA_THAT_IS_GOING_TO_BE_UPLOADED_TO_INSTAGRAM: str = (
    "Media that is going to be uploaded to Instagram")
TITLE_OF_YOUR_IGTV: str = "Title Of Your IGTV"
CAPTION_THAT_IS_GOING_TO_BE_UPLOADED_TO_INSTAGRAM: str = (
    "Caption that is going to be uploaded to Instagram")
YOUR_CONTENT_IS_SUCCESSFULLY_UPLOADED_TO_INSTAGRAM: str = (
    "Your content is successfully uploaded to Instagram and you can "
    "access it with the following link:\n"
    "{media_url}\n"
    "\n"
    "{instagram_assistant_id}")
UPLOAD_WAS_CANCELED_BY_THE_USER: str = "Upload was canceled by the user"
SOMETHING_WENT_WRONG: str = "Something Went Wrong"
FILE_IS_NOT_VALID: str = "File is not valid, You must be uploaded image or gif"
OK_SEND_ME_THE_LINK_YOU_WANT_TO_DOWNLOAD: str = "OK, send me the link you want to download from Instagram Such Profile, Post, Story and etc... or for Download Profile Picture Send Username With @ Such @Username"
SEND_THE_POST_LINK_YOU_WANT_TO_GET_THE_STATISTICS: str = "Send the post link you want to get the statistics or send instagram username such @username for getting user info"
PLEASE_WAIT_A_FEW_MINUTES_BEFORE_YOU_TRY_AGAIN: str = (
    "Please wait a few minutes before you try again")
UPLOADED_IMAGE_ISNT_IN_AN_ALLOWED_ASPECT_RATIO: str = (
    "Uploaded image isn't in an allowed aspect ratio")
INSIGHT_OF_MEDIA: str = ("Post statistics:\n"
                         "Like Count: {like_count}\n"
                         "Comment Count: {comment_count}\n"
                         "Save Count: {save_count}\n"
                         "Share Count: {share_count}\n"
                         "\n"
                         "{instagram_assistant_id}")
WELCOME_TO_ADMIN: str = ("Welcome To Admin\n\n"
                         "Follow the procedure to Setup Your bot\n\n"
                         "<b>Twitter 💬</b>\n"
                         "<em>Search 🔎</em>\n"
                         "-You have to set the keywords that will be stored in the bot.\n"
                         "-These will be used for the Competition so you have to set it first\n\n"
                         "<em>Send 💬</em>\n"
                         "-These get and forward tweets based on the keywords searched\n\n"
                         "<em>Stop ✋</em>\n"
                         "-These stop the bot from forwarding tweets to groups\n\n"
                         "<b>Comp 🏆</b>\n"
                         "<em>Setup points</em>\n"
                         "-These is where you setup the points for the competition\n\n"
                         "<em>Start</em>\n"
                         "-These starts the competition\n\n"
                         "<em>Stop ✋</em>\n"
                         "-These stops the competition\n\n"
                         "<em>Leaderboard 📊</em>\n"
                         "<em>Time Interval</em>\n"
                         "-Set the time interval used to display the Leaderboard.\n\n"
                         "<em>Display</em>\n"
                         "-Display the Leaderboard based on the time interval\n\n"
                         "<em>Hide</em>\n"
                         "-Hides the Leaderboard, it won't be displayed in groups\n\n"
                         "<em>Send Token to winners</em>\n"
                         "<em>Set prize</em>\n"
                         "-Set the prize for each position in the competition\n\n"
                         "<em>Change prize</em>\n"
                         "-Change the prize that has already been set.\n\n"
                         "<em>Send Token</em>\n"
                         "Sent tokens to Winners base on the prize set, <b>Please Stop the competition before sending tokens</b>\n\n"
                         "<em>Participant 👨‍💼</em>\n"
                         "<em>View Participant</em>\n"
                         "-View all Participants for the Competition\n\n"
                         "<em>Ban Participant</em>\n"
                         "-Ban Participants\n\n"
                         "<b>Wallet 💰</b>\n"
                         "<em>Create Wallet 💰</em>\n"
                         "-Creates Wallet for the admin\n\n"
                         "<em>Wallet Details 📝</em>\n"
                         "-Sends Admin wallet Details\n\n"
                         "<em>Delete Wallet 🚮</em>\n"
                         "-Deletes Admin Wallet\n"
)
USER_COUNT: str = "User Count: {user_count}"
WELCOME_TO_HOME: str = "Welcome To Home, What are you doing?"
SEND_YOUR_MESSAGE: str = "Send Your Message 👇"
YOUR_MESSAGE_WAS_SENT: str = "Your Message Was Sent"
PRIVACY_MESSAGE: str = (
    "⚠️ The MILC Commmunity Bot will store the following Telegram information:\n"
    "User ID, First Name, Last Name, Username\n"
    "\n"
    "If you wish to enter the competition, you will need to provide your BSC wallet address and Twitter credentials to verify your entry."
    )
WELCOME_TO_THE_TWITTER_SECTION: str = (
    "Welcome to the Twitter section.\n"
    "Choose the topic to Search and then tap on Send 💬")
WELL_YOU_WANT_TO_DO_THE_LOTTERY_ON_WHAT_BASIS: str = (
    "Well you want to do the lottery on what basis:")
REMEMBER_ME: str = "Is your session saved for the next login?"
USER_NOT_FOUND_CHECK_USERNAME_AND_TRY_AGAIN: str = (
    "User not found, check username and try again")
PLEASE_SEND_PHOTO_OR_VIDEO: str = "file is not valid, please send a photo (Support JPG files) or video (Support MP4 files)"
GETTING_STORY_INFORMATION: str = "Getting Story information ..."
GETTING_MEDIA_INFORMATION: str = "Getting media information ..."
GETTING_PROFILE_INFORMATION: str = "Getting profile information ..."
THIS_ROBOT_SAVES_A_SESSION_FOR_NEXT_LOGIN_IF_YOU_WANT: str = (
    "⚠️ Attention: This robot saves a session for next Login if you want")
BOT_UNDER_MAINTENANCE: str = "Bot Under Maintenance 🛠️\nThank you for waiting"
MEDIA_NOT_FOUND: str = (
    "Media Not Found or Unavailable, Please Check Your Link And Try Again")
RULE_MESSAGE: str = """
Hi {first_name}, in order to activate the MILC Community Bot you must read and accept the following rules before you can interact with it.\n
{rule_message}\n
\n
Do you accept the privacy policy of this robot? (Select Yes / No)
"""
GOODBYE_WE_ARE_SORRY: str = (
    "Goodbye, we are sorry that we couldn't create a good experience for you")
SENDING_THUMBNAIL: str = "Sending thumbnail ..."
SENDING_VIDEO: str = "Sending Video ..."
USER_INFO: str = """
{username} Info:\n
Full Name: {full_name}\n
Biography:\n {biography}\n
Following: {following}\n
Follower: {follower}\n
Media Count: {media_count}\n
{instagram_assistant_id}
"""
INSTAGRAM_COM: str = "instagram.com"
PLEASE_SEND_THE_INSTAGRAM_LINK: str = "Link is Invalid, Please Send The Instagram Link With Domain instagram.com and Try Again"
FEEDBACK_MESSAGE: str = (
    "Welcome To Feedback Section\n"
    "You can send us any comments or criticisms or suggestions")
NEW_MESSAGE: str = (
    "Have a new message From [{first_name}](tg://user?id={user_id}) \n"
    "User Information:\n}"
    "User ID: {user_id}"
    "first name: {first_name}\n"
    "last name: {last_name}\n"
    "username: @{username}\n")
NEW_TEXT_MESSAGE: str = (
    "Have a new message From [{first_name}](tg://user?id={user_id}) \n"
    "Message: {message} \n"
    "User Information:\n"
    "User ID: {user_id}\n"
    "first name: {first_name}\n"
    "last name: {last_name}\n"
    "username: @{username}\n")
YOUR_MESSAGE_WAS_SENT: str = "your message was sent\nThank For Submit Feedback 🙏"
MEDIA_CAPTION: str = "{caption}\n\n{instagram_assistant_id}"
CHALLENGE_REQUIRED: str = "Challenge Required, Please Try Again A few Moment Later"
YOU_NEED_TO_LOGIN_AGAIN: str = "You need to login again!"
