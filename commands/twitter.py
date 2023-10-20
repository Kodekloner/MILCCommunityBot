import asyncio
import os
import html
import requests
import shutil
import re
import json
from datetime import datetime, timedelta
from typing import Dict
from requests_oauthlib import OAuth1

from logging import getLogger

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import time

import commands
from config.db import sqlite_conn
from config import logger
from utils.decorators import description, example, triggers, usage

from config.options import config

# Init logger
logger = getLogger(__name__)


bearer_token = config["API"]["TWITTER_BEARER_TOKEN"]
access_token = config["API"]["TWITTER_ACCESS_TOKEN"]
access_token_secret = config["API"]["TWITTER_ACCESS_TOKEN_SECRET"]
api_key = config["API"]["TWITTER_API_KEY"]
key_secret = config["API"]["TWITTER_KEY_SECRET"]


def make_api_request_with_backoff(context: ContextTypes.DEFAULT_TYPE, endpoint, headers, params=None):
    if params == None:
        response = requests.get(endpoint, headers=headers)
    else:
        response = requests.get(endpoint, params=params, headers=headers)

    if response.status_code == 200:
        remaining_requests = int(response.headers.get('x-rate-limit-remaining'))
        reset_time = int(response.headers.get('x-rate-limit-reset'))
        return response.json(), remaining_requests, reset_time
    else:
        print(response.status_code)
        print(response.text)
        message = f"{response.status_code}\n\n{response.text}"
        if (
            "LOGGING_CHANNEL_ID" in config["TELEGRAM"]
            and config["TELEGRAM"]["LOGGING_CHANNEL_ID"]
        ):
            # Finally, send the message
            context.bot.send_message(
                chat_id=config["TELEGRAM"]["LOGGING_CHANNEL_ID"],
                text=message,
                parse_mode=ParseMode.HTML,
            )
        return None, None, None

def wait_for_rate_limit(remaining_requests, reset_time):
    print(f"Remaining requests: {remaining_requests}")
    print(f"Reset time: {reset_time}")

    if remaining_requests == 0:
        current_time = time.time()
        sleep_time = reset_time - current_time + 5  # Adding extra 5 seconds buffer
        return sleep_time
    else:
        return 0


async def get_tweets(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get tweet """
    job_queue = context.job_queue
    job = context.job

    endpoint = 'https://api.twitter.com/2/tweets/search/recent'
    headers = {'authorization': f'Bearer {bearer_token}'}

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM TwitterSearch")

    result = cursor.fetchone()

    # Get the current time
    current_time = datetime.utcnow()

    # Subtract one day
    one_day_ago = current_time - timedelta(hours=3)

    # Format the datetime object as ISO 8601/RFC 3339
    iso_format = one_day_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

    if result:
        # search = " OR ".join(result["word"].split())
        search = result["word"].strip()
        since_id = result["since_id"]
        # query = f'(crypto, {search}) -is:retweet -is:reply lang:en'
        query = f'({search}) -is:retweet -is:reply lang:en'
        if since_id == "" or since_id is None:
            params = {
                'query': query,
                'max_results': '100',
                'tweet.fields': 'created_at,text,attachments,author_id',
                'expansions': 'attachments.media_keys,author_id',
                'media.fields': 'preview_image_url,url',
                'user.fields': 'username',
                'start_time': iso_format
            }
        else:
            params = {
                'query': query,
                'max_results': '100',
                'tweet.fields': 'created_at,text,attachments,author_id',
                'expansions': 'attachments.media_keys,author_id',
                'media.fields': 'preview_image_url,url',
                'user.fields': 'username',
                'since_id': since_id
            }

        response = requests.get(endpoint, params=params, headers=headers)

        if response.status_code == 200:
            response_data = response.json()

            if not job.data:
                await context.bot.send_message(job.chat_id,
                    "Successful, Bot will start storing tweets regularily\n",
                )
                job.data = True

            # print(json.dumps(response.json(), indent=2, sort_keys = True))
            # print(response_data)

            if "data" in response_data:
                for tweet in response_data["data"]:
                    tweet_id = tweet["id"]
                    photo_url = ''
                    tweet_text = tweet["text"]
                    created_at = tweet["created_at"]

                    if "attachments" in tweet:
                        if "media_keys" in tweet['attachments']:
                            attachments_media_keys = tweet['attachments']['media_keys']
                            for media in response_data["includes"]["media"]:
                                if media["media_key"] == attachments_media_keys[0]:
                                    if "url" in media:
                                        photo_url = media["url"]
                                    elif "preview_image_url" in media:
                                        photo_url = media["preview_image_url"]

                    if tweet["author_id"]:
                        author_id = tweet["author_id"]
                        for users in response_data["includes"]["users"]:
                            if users["id"] == author_id:
                                username = users["username"]

                    cursor.execute(
                        """INSERT INTO tweets (tw_id, tweets, images, created_at, username, sent) VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            tweet_id,
                            tweet_text,
                            photo_url,
                            created_at,
                            username,
                            False,
                        ),
                    )

                # Update the 'sent' value to True
                cursor.execute("UPDATE TwitterSearch SET since_id=? WHERE id=?", (response_data["meta"]["newest_id"], 1))
            # Commit the changes
            sqlite_conn.commit()

            # # Close the database connection
            # sqlite_conn.close()

        else:
            if any(job.callback == get_tweets or job.callback == send_tweets for job in job_queue.jobs()):
                for job in job_queue.jobs():
                    if job.callback == get_tweets or job.callback == send_tweets:
                        job.schedule_removal()

            await context.bot.send_message(job.chat_id,
                "❌ <b>There was an Error with your keywords combination</b>\n"
                "check your keywords and send again",
                parse_mode=ParseMode.HTML,
            )
            print(response.status_code)
            print(response.text)

    else:
        if any(job.callback == get_tweets or job.callback == send_tweets for job in job_queue.jobs()):
            for job in job_queue.jobs():
                if job.callback == get_tweets or job.callback == send_tweets:
                    job.schedule_removal()

        await context.bot.send_message(job.chat_id,
            "<b>❌ Please set the Keywords</b>\n"
            "and send the again",
            parse_mode=ParseMode.HTML,
        )

async def leaderboard(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get tweet """
    job = context.job

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM tweets")
    results = cursor.fetchall()

    cursor.execute("SELECT * FROM point_system")
    point_system = cursor.fetchone()

    tweets_username_counts = {}
    liking_username_counts = {}
    retweeted_username_counts = {}
    repling_username_counts = {}

    user_scores = {}

    if results:
        current_time = datetime.utcnow()

        # Subtract one day from the current timestamp
        previous_day = current_time - timedelta(days=1)
        for result in results:
            sent_time = result['sent_at']
            sent = result['sent']

            sent_time = datetime.strptime(sent_time, '%Y-%m-%d %H:%M:%S.%f')
            print(sent_time)
            print(previous_day)

            if sent_time >= previous_day and sent == 1:
                tweet_id = result['tw_id']
                headers = {'authorization': f'Bearer {bearer_token}'}

                # users that retweeted
                retweeted_endpoint = f'https://api.twitter.com/2/tweets/{tweet_id}/retweeted_by'
                retweeted_response, remaining_requests, reset_time = make_api_request_with_backoff(context, retweeted_endpoint, headers=headers)

                if retweeted_response is not None:
                    print("retweeted")
                    print(json.dumps(retweeted_response, indent=2, sort_keys = True))
                    print()
                    if "data" in retweeted_response:
                        for usernames in retweeted_response["data"]:
                            username = usernames["username"]
                            retweeted_username_counts[username] = retweeted_username_counts.get(username, 0) + 1

                sleep_time = wait_for_rate_limit(remaining_requests, reset_time)
                if sleep_time > 0:
                    print(f"Rate limit reached. Waiting for {sleep_time:.2f} seconds until reset time...")
                    message = f"Rate limit reached. Waiting for {sleep_time:.2f} seconds until reset time..."
                    if (
                        "LOGGING_CHANNEL_ID" in config["TELEGRAM"]
                        and config["TELEGRAM"]["LOGGING_CHANNEL_ID"]
                    ):
                        # Finally, send the message
                        await context.bot.send_message(
                            chat_id=config["TELEGRAM"]["LOGGING_CHANNEL_ID"],
                            text=message,
                            parse_mode=ParseMode.HTML,
                        )
                    time.sleep(sleep_time)

                #users that liked
                liking_endpoint = f'https://api.twitter.com/2/tweets/{tweet_id}/liking_users'
                liking_response, remaining_requests, reset_time = make_api_request_with_backoff(context, liking_endpoint, headers=headers)

                if liking_response is not None:
                    print("liked")
                    print(json.dumps(liking_response, indent=2, sort_keys = True))
                    print()
                    if "data" in liking_response:
                        for usernames in liking_response["data"]:
                            username = usernames["username"]
                            liking_username_counts[username] = liking_username_counts.get(username, 0) + 1

                sleep_time = wait_for_rate_limit(remaining_requests, reset_time)
                if sleep_time > 0:
                    print(f"Rate limit reached. Waiting for {sleep_time:.2f} seconds until reset time...")
                    message = f"Rate limit reached. Waiting for {sleep_time:.2f} seconds until reset time..."
                    if (
                        "LOGGING_CHANNEL_ID" in config["TELEGRAM"]
                        and config["TELEGRAM"]["LOGGING_CHANNEL_ID"]
                    ):
                        # Finally, send the message
                        await context.bot.send_message(
                            chat_id=config["TELEGRAM"]["LOGGING_CHANNEL_ID"],
                            text=message,
                            parse_mode=ParseMode.HTML,
                        )
                    time.sleep(sleep_time)

                #users that replies
                replies_endpoint = 'https://api.twitter.com/2/tweets/search/recent'
                query = f'conversation_id:{tweet_id}'

                params = {
                    'query': query,
                    'max_results': '100',
                    'tweet.fields': 'author_id',
                    'expansions': 'author_id'
                }

                # time.sleep(2.4)
                response, remaining_requests, reset_time = make_api_request_with_backoff(context, replies_endpoint, params=params, headers=headers)

                if response is not None:
                    print("replies")
                    print(json.dumps(response, indent=2, sort_keys = True))
                    print()

                    if "data" in response:
                        for tweet in response["data"]:
                            if tweet["author_id"]:
                                author_id = tweet["author_id"]
                                for users in response["includes"]["users"]:
                                    if users["id"] == author_id:
                                        username = users["username"]
                                        repling_username_counts[username] = repling_username_counts.get(username, 0) + 1

                sleep_time = wait_for_rate_limit(remaining_requests, reset_time)
                if sleep_time > 0:
                    print(f"Rate limit reached. Waiting for {sleep_time:.2f} seconds until reset time...")
                    message = f"Rate limit reached. Waiting for {sleep_time:.2f} seconds until reset time..."
                    if (
                        "LOGGING_CHANNEL_ID" in config["TELEGRAM"]
                        and config["TELEGRAM"]["LOGGING_CHANNEL_ID"]
                    ):
                        # Finally, send the message
                        await context.bot.send_message(
                            chat_id=config["TELEGRAM"]["LOGGING_CHANNEL_ID"],
                            text=message,
                            parse_mode=ParseMode.HTML,
                        )
                    time.sleep(sleep_time)


                username = result['username']
                tweets_username_counts[username] = tweets_username_counts.get(username, 0) + 1

        # Loop through tweet_username dictionary
        for username, count in tweets_username_counts.items():
            user_scores[username] = user_scores.get(username, 0) + (point_system['tweets'] * count)

        # Loop through reply_username dictionary
        for username, count in repling_username_counts.items():
            user_scores[username] = user_scores.get(username, 0) + (point_system['replies'] * count)

        # Loop through like_username dictionary
        for username, count in liking_username_counts.items():
            user_scores[username] = user_scores.get(username, 0) + (point_system['likes'] * count)

        # Loop through retweet_username dictionary
        for username, count in retweeted_username_counts.items():
            user_scores[username] = user_scores.get(username, 0) + (point_system['retweets'] * count)

        # Iterate over the combined counts and insert them into the table
        for username, score in user_scores.items():
            tweets = tweets_username_counts.get(username, 0)
            likes = liking_username_counts.get(username, 0)
            retweets = retweeted_username_counts.get(username, 0)
            replies = repling_username_counts.get(username, 0)
            # quotes = quote_username_counts.get(username, 0)
            total = score

            # Update the scores for existing users
            cursor.execute('UPDATE leaderboard SET tweets = tweets + ?, replies = replies + ?, likes = likes + ?, retweets = retweets + ?, total = total + ? WHERE username = ?',
                           (tweets, replies, likes, retweets, total, username))
            sqlite_conn.commit()

            # Insert new users
            cursor.execute('INSERT INTO leaderboard (username, tweets, replies, likes, retweets, total) SELECT ?, ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM leaderboard WHERE username = ?)',
                           (username, tweets, replies, likes, retweets, total, username))
            sqlite_conn.commit()

        if not job.data:
            await context.bot.send_message(job.chat_id,
                "<b>Competition Started Successfully\n</b>"
                "Display the leaderboard to groups.",
                parse_mode=ParseMode.HTML,
            )
            job.data = True

        message = "<b>Competition Scores calculated Successfully\n</b>"
        if (
            "LOGGING_CHANNEL_ID" in config["TELEGRAM"]
            and config["TELEGRAM"]["LOGGING_CHANNEL_ID"]
        ):
            # Finally, send the message
            await context.bot.send_message(
                chat_id=config["TELEGRAM"]["LOGGING_CHANNEL_ID"],
                text=message,
                parse_mode=ParseMode.HTML,
            )

    else:
        await context.bot.send_message(job.chat_id,
            "<b>❌ No tweets yet base on the keywords for the competition\n</b>",
            parse_mode=ParseMode.HTML,
        )

async def send_tweets(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    cursor = sqlite_conn.cursor()
    if not job.data[2]:
        await context.bot.send_message(job.chat_id,
            "Success! The selected group will receive tweets.",
        )
        job.data[2] = True
    cursor.execute("SELECT DISTINCT chat_id FROM chat_stats WHERE type LIKE '%group%' AND title = ?;", (job.data[3],),)
    result = cursor.fetchone()

    if result:
        cursor.execute(
            """
            SELECT * FROM `tweets` WHERE sent = ? ORDER BY id DESC LIMIT 5
            """,
            (False,),
        )

        rows = cursor.fetchall()

        if not rows:
            return

        sent_time = datetime.utcnow()
        print(sent_time)

        influencers = ""
        for index, row in enumerate(rows, start=1):
            tweet_status_id = row["tw_id"]
            screen_name = row["username"]

            # Check if it is the last row
            if index == len(rows):
                username = f'<a href="https://twitter.com/i/status/{tweet_status_id}">{screen_name}</a>'
                last_index = index  # Store the last index
            else:
                username = f'<a href="https://twitter.com/i/status/{tweet_status_id}">{screen_name}</a> || '

            influencers += username

            cursor.execute(
                """
                UPDATE tweets SET sent=?, sent_at=? WHERE id=?;
                """,
                (True, sent_time, row['id']),
            )

        message = f"🚀 Let's raid the following Tweet(s) 🚀\n\n" +  influencers + "\n\n‼️ To spread the word faster just click on the link and you will be directed to the Tweet ‼️\n"

        if job.data[1] == "Photo":
            # await context.bot.send_photo(result['chat_id'], photo=image_url, caption=tweet_text)
            await context.bot.send_photo(result['chat_id'], photo=job.data[0], caption=message, parse_mode=ParseMode.HTML,)
        elif job.data[1] == "Gif":
            # await context.bot.send_photo(result['chat_id'], photo=image_url, caption=tweet_text)
            await context.bot.send_animation(result['chat_id'], animation=job.data[0], caption=message, parse_mode=ParseMode.HTML,)

async def display_board(context: ContextTypes.DEFAULT_TYPE) -> None:
    job_queue = context.job_queue
    job = context.job
    cursor = sqlite_conn.cursor()

    # Fetch the distinct group_id and channel_id values
    cursor.execute("SELECT DISTINCT chat_id FROM chat_stats WHERE type LIKE '%group%' AND title = ?;", (job.data[2],),)
    distinct_id = cursor.fetchone()

    if distinct_id:
        group_chat_id = distinct_id["chat_id"]

        cursor.execute("SELECT * FROM user_wallet_twitter WHERE telegram_group = ?;", (job.data[2],),)
        participates = cursor.fetchall()

        if not participates:
            await context.bot.send_message(job.chat_id,
                "❌You don't have participant yet for the selected group",
            )
            job.data[0] = True
            return

        leaderboard = {}
        for participate in participates:
            if participate['username'] != None:
                    p_user = participate['username']
            else:
                p_user = participate['first_name']
            p_tuser = participate['twitter_username']
            cursor.execute(
                """
                SELECT user_wallet_twitter.username, user_wallet_twitter.twitter_username, user_wallet_twitter.chat_id, leaderboard.id, leaderboard.tweets, leaderboard.replies, leaderboard.likes, leaderboard.retweets, leaderboard.total
                FROM leaderboard
                JOIN user_wallet_twitter ON leaderboard.username = user_wallet_twitter.twitter_username
                WHERE user_wallet_twitter.ban = ? AND user_wallet_twitter.telegram_group = ?
                ORDER BY leaderboard.total DESC
                """,
                (False, job.data[2]),
            )
            rows = cursor.fetchall()

            if rows:
                for row in rows:
                    b_name = row['twitter_username']
                    if p_tuser == b_name:
                        leaderboard[p_user] = row["total"]
                        break
                    else:
                        leaderboard[p_user] = 0
            else:
                leaderboard[p_user] = 0

        # Rearrange the leaderboard dictionary based on values in descending order
        leaderboard = dict(sorted(leaderboard.items(), key=lambda x: x[1], reverse=True))

        if not job.data[1]:
            await context.bot.send_message(job.chat_id,
                "Successful, the competition leaderboard will be displayed at the set time",
            )
            job.data[1] = True
        # Prepare the leaderboard message
        message = "<b>Leaderboard:</b>\n\n"

        for i, (username, score) in enumerate(leaderboard.items(), start=1):
            entry = f"{i}. <b>{username}</b>: {score}\n"
            message += entry

        # Add emojis and formatting
        message = "🏆📊 <b>Leaderboard</b> 📊🏆\n\n" + message

        # Send the message to the appropriate group or channel
        await context.bot.send_message(group_chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
        )
