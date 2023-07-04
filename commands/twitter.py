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


from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from time import sleep

import commands
from config.db import sqlite_conn
from config import logger
from utils.decorators import description, example, triggers, usage

from config.options import config



bearer_token = config["API"]["TWITTER_BEARER_TOKEN"]
access_token = config["API"]["TWITTER_ACCESS_TOKEN"]
access_token_secret = config["API"]["TWITTER_ACCESS_TOKEN_SECRET"]
api_key = config["API"]["TWITTER_API_KEY"]
key_secret = config["API"]["TWITTER_KEY_SECRET"]


def generate_oauth1_header():
    oauth1_auth = OAuth1(
        api_key,
        key_secret,
        access_token,
        access_token_secret
    )
    return oauth1_auth

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
    one_day_ago = current_time - timedelta(days=1)

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
    quote_username_counts = {}

    user_scores = {}

    if results:
        for result in results:
            created_time = result['created_at']
            started_time = job.data[0]

            created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S.%fZ')

            if created_time >= started_time:
                tweet_id = result['tw_id']
                headers = {'authorization': f'Bearer {bearer_token}'}

                # users that retweeted
                retweeted_endpoint = f'https://api.twitter.com/2/tweets/{tweet_id}/retweeted_by'
                sleep(14.5)
                retweeted_response = requests.get(retweeted_endpoint, headers=headers)

                if retweeted_response.status_code == 200:
                    response_data = retweeted_response.json()

                    print(json.dumps(retweeted_response.json(), indent=2, sort_keys = True))

                    if "data" in response_data:
                        for usernames in response_data["data"]:
                            username = usernames["username"]
                            retweeted_username_counts[username] = retweeted_username_counts.get(username, 0) + 1


                #users that liked
                liking_endpoint = f'https://api.twitter.com/2/tweets/{tweet_id}/liking_users'

                sleep(14.5)
                liking_response = requests.get(liking_endpoint, headers=headers)

                if liking_response.status_code == 200:
                    response_data = liking_response.json()

                    print(json.dumps(liking_response.json(), indent=2, sort_keys = True))

                    if "data" in response_data:
                        for usernames in response_data["data"]:
                            username = usernames["username"]
                            liking_username_counts[username] = liking_username_counts.get(username, 0) + 1


                #users that replies
                replies_endpoint = 'https://api.twitter.com/2/tweets/search/recent'
                query = f'conversation_id:{tweet_id}'

                params = {
                    'query': query,
                    'max_results': '100',
                    'tweet.fields': 'author_id',
                    'expansions': 'author_id'
                }

                sleep(2.4)
                response = requests.get(replies_endpoint, params=params, headers=headers)

                if response.status_code == 200:
                    response_data = response.json()

                    print(json.dumps(response.json(), indent=2, sort_keys = True))

                    if "data" in response_data:
                        for tweet in response_data["data"]:

                            if tweet["author_id"]:
                                author_id = tweet["author_id"]
                                for users in response_data["includes"]["users"]:
                                    if users["id"] == author_id:
                                        username = users["username"]
                                        repling_username_counts[username] = repling_username_counts.get(username, 0) + 1
                else:
                    print(response.status_code)
                    print(response.text)


                # users that quoted a tweet
                quote_endpoint = f'https://api.twitter.com/2/tweets/{tweet_id}/quote_tweets'
                params = {
                    'query': query,
                    'max_results': '100',
                    'tweet.fields': 'author_id',
                    'expansions': 'author_id'
                }
                sleep(14.5)
                quote_response = requests.get(quote_endpoint, params=params, headers=headers)

                if quote_response.status_code == 200:
                    response_data = quote_response.json()

                    print(json.dumps(quote_response.json(), indent=2, sort_keys = True))

                    if "data" in response_data:
                        for usernames in response_data["data"]:
                            username = usernames["username"]
                            quote_username_counts[username] = quote_username_counts.get(username, 0) + 1


                username = result['username']
                tweets_username_counts[username] = tweets_username_counts.get(username, 0) + 1

        print(tweets_username_counts)
        print("_______________________")
        print(liking_username_counts)
        print("_______________________")
        print(retweeted_username_counts)
        print("_______________________")
        print(repling_username_counts)
        print("_______________________")
        print(quote_username_counts)

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

        # Loop through quote_username dictionary
        for username, count in quote_username_counts.items():
            user_scores[username] = user_scores.get(username, 0) + (point_system['quote'] * count)


        # Execute a query to fetch data from the table
        cursor.execute("SELECT COUNT(*) FROM leaderboard")
        result = cursor.fetchone()

        # Check if the table is empty
        if result[0] == 0:

            # Iterate over the combined counts and insert them into the table
            for username, score in user_scores.items():
                tweets = tweets_username_counts.get(username, 0)
                likes = liking_username_counts.get(username, 0)
                retweets = retweeted_username_counts.get(username, 0)
                replies = repling_username_counts.get(username, 0)
                quotes = quote_username_counts.get(username, 0)
                total = score

                cursor.execute('INSERT INTO leaderboard (username, tweets, replies, likes, retweets, quotes, total) VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (username, tweets, replies, likes, retweets, quotes, total))
                sqlite_conn.commit()
        else:
            # Table is not empty, remove current data and add new ones
            cursor.execute("DELETE FROM leaderboard")
            # Perform your insert operation here
            for username, score in user_scores.items():
                tweets = tweets_username_counts.get(username, 0)
                likes = liking_username_counts.get(username, 0)
                retweets = retweeted_username_counts.get(username, 0)
                replies = repling_username_counts.get(username, 0)
                quotes = quote_username_counts.get(username, 0)
                total = score

                cursor.execute('INSERT INTO leaderboard VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (username, tweets, replies, likes, retweets, quotes, total))
                sqlite_conn.commit()

        if not job.data[1]:
            await context.bot.send_message(job.chat_id,
                "<b>Competition Started Successfully\n</b>"
                "Display the leaderboard to groups.",
                parse_mode=ParseMode.HTML,
            )
            job.data[1] = True

    else:
        await context.bot.send_message(job.chat_id,
            "<b>❌ No tweets yet base on the keywords for the competition\n</b>"
            "Will check in the next 20mins",
            parse_mode=ParseMode.HTML,
        )

async def send_tweets(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    cursor = sqlite_conn.cursor()
    if not job.data[2]:
        await context.bot.send_message(job.chat_id,
            "Successful, the selected group will start receiving tweets messages",
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

        influencers = ""
        for index, row in enumerate(rows, start=1):
            tweet_status_id = row["tw_id"]
            screen_name = row["username"]

            # Check if it is the last row
            if index == len(rows):
                username = f'<a href="https://twitter.com/i/web/status/{tweet_status_id}">{screen_name}</a>'
                last_index = index  # Store the last index
            else:
                username = f'<a href="https://twitter.com/i/web/status/{tweet_status_id}">{screen_name}</a> || '

            influencers += username

            cursor.execute(
                """
                UPDATE tweets SET sent=? WHERE id=?;
                """,
                (True, row['id']),
            )

        message = f"🚀 Let's Raid these {last_index} new tweets\n\n" +  influencers + "\n\n📢 To spread the word faster\n\nJust click on the influencers above, you will be directed to their tweet\n"

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

        cursor.execute(
            """
            SELECT user_wallet_twitter.username, user_wallet_twitter.chat_id, leaderboard.id, leaderboard.tweets, leaderboard.replies, leaderboard.likes, leaderboard.retweets, leaderboard.quotes, leaderboard.total
            FROM leaderboard
            JOIN user_wallet_twitter ON leaderboard.username = user_wallet_twitter.twitter_username
            WHERE user_wallet_twitter.ban = ? AND user_wallet_twitter.chat_id = ?
            ORDER BY leaderboard.total DESC
            """,
            (False, group_chat_id),
        )
        rows = cursor.fetchall()

        if not rows:
            if not job.data[0]:
                await context.bot.send_message(job.chat_id,
                    "❌You don't have Participant yet for the Competition",
                )
                job.data[0] = True
                return

        if not job.data[1]:
            await context.bot.send_message(job.chat_id,
                "Successful, the Competition Leaderboard will be displayed at the set time",
            )
            job.data[1] = True
        # Prepare the leaderboard message
        message = "<b>Leaderboard:</b>\n\n"

        for index, row in enumerate(rows, start=1):
            username = row["username"]
            total = row["total"]
            entry = f"{index}. <b>{username}</b>: {total}\n"
            message += entry

        # Add emojis and formatting
        message = "🏆📊 <b>Leaderboard</b> 📊🏆\n\n" + message

        # Send the message to the appropriate group or channel
        await context.bot.send_message(group_chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
        )
