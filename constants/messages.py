SET_POINT_SYSTEM_WITH_POINTS: str = (
    "Each *Tweet* is {tweet} point(s).\n"
    "Each *reply* is {reply} point(s).\n"
    "Each *like* is {like} point(s).\n"
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
    "Please change the competition points in the following format:\n"
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
    "Please enter the competition price in the following format: \n"
    '"position"-"prize" - Example:\n'
    "\n"
    "1-5.002\n"
    "4-4\n"
    "\n"
    "<b>Note:</b> This price can be any value, but the first number is the position, the number after the '-' is the prize."
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
WHAT_DO_YOU_WANT: str = "what do you want ?"
WELCOME_MESSAGE: str = (
    "Hello {first_name}, welcome to MILC Community Bot.\n"
    "\n"
    "**Before we start, what can the Bot actually do?**\n"
    "\n"
    "MILC Community Bot allows you to earn rewards by promoting and spreading the word about the MILC project on Twitter. To make this work, the Bot has a competition function and integrated reward distributions.\n"
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

FILE_IS_NOT_VALID: str = "File is not valid, You must be uploaded image or gif"
WELCOME_TO_ADMIN: str = ("<b>Welcome to admin section</b>\n\n"
                         "Follow the procedure to set up the Bot\n\n"
                         "<b>Twitter button💬</b>\n\n"
                         "<em>Search function🔎</em>\n"
                         "- You have to set the keywords that will be stored in the Bot. These will be used for the competition, so you must set them first.\n\n"
                         "<em>Send function💬</em>\n"
                         "- This function stores and forwards the Tweets based on the keywords searched for.\n\n"
                         "<em>Upload Photo function📤</em>\n"
                         "- With this function, you can upload a photo or GIF that is forwarded with the Tweets.\n\n"
                         "<em>Stop function✋</em>\n"
                         "- This function stops the Bot from forwarding the Tweets to the groups.\n\n"
                         "<b>Comp button🏆</b>\n\n"
                         "<em>Setup points</em>\n"
                         "- This function defines the points to be distributed depending on the action.\n\n"
                         "<em>Start</em>\n"
                         "- This function launches the competition\n\n"
                         "<em>Stop ✋</em>\n"
                         "- This function stops the competition\n\n"
                         "<em>Leaderboard 📊</em>\n"
                         "- This function allows you to modify and start the leaderboard\n\n"
                         "<em>Time Interval</em>\n"
                         "- Define the time interval to display the leaderboard.\n\n"
                         "<em>Display</em>\n"
                         "- Select the groups where the leaderboard should be displayed\n\n"
                         "<em>Hide</em>\n"
                         "- Hide the ranking - it will then no longer be displayed in the groups\n\n"
                         "<em>Send Token to winners 💰</em>\n"
                         "- This function allows you to modify and execute the distribution function.\n\n"
                         "<em>Set prize</em>\n"
                         "- Define the award amounts according to the leaderboard position.\n\n"
                         "<em>Change prize</em>\n"
                         "- Change the prize money according to the ranking.\n\n"
                         "<em>Send Token</em>\n"
                         "- This will send the tokens to the winners based on the award, <b>please close the competition before sending the tokens.</b>\n\n"
                         "<em>Participant(s) 👨‍💼</em>\n"
                         "- This function allows you to manage the participants.\n\n"
                         "<em>View Participant(s)</em>\n"
                         "- Here you can view all participants.\n\n"
                         "<em>Ban Participant(s)</em>\n"
                         "- Here you can ban participants.\n\n"
                         "<b>Wallet 💰</b>\n\n"
                         "<em>Create Wallet 💰</em>\n"
                         "- Creates a wallet\n\n"
                         "<em>Wallet Details 📝</em>\n"
                         "- Displays the wallet details\n\n"
                         "<em>Delete Wallet 🚮</em>\n"
                         "- Deletes the wallet\n"
)
USER_COUNT: str = "User Count: {user_count}"
WELCOME_TO_HOME: str = "Welcome home, what do you want to do?"
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
    "Select the keyword you want to search and then tap send.")
PLEASE_SEND_PHOTO_OR_VIDEO: str = "file is not valid, please send a photo (Support JPG files) or video (Support MP4 files)"
BOT_UNDER_MAINTENANCE: str = "Bot Under Maintenance 🛠️\nThank you for waiting"
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
