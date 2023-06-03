import asyncio
import os
import requests
import shutil
from typing import Dict

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from Scrapetwitter.scrapetwitter import Scrapetwitter

from time import sleep

import commands
from config.db import sqlite_conn
from config import logger
from utils.decorators import description, example, triggers, usage


async def get_tweets(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get tweet """
    job = context.job
    try:
        with Scrapetwitter() as bot:
            bot.login()
            articles = bot.search()
            bot.get_tweets()
    except Exception as e:
        if 'in PATH' in str(e):
            print(
                "You are trying to run the bot from command line \n"
                "Please add to PATH your Selenium Drivers \n"
                "Windows: \n"
                "   set PATH=%PATH%;C:path-to-your-folder \n \n"
                "Linux: \n"
                "   PATH=$PATH:/path/toyour/folder/ \n"
            )
        else:
            raise

async def get_user_replies(time) -> Dict[str, any]:
    """Get tweet user replies"""
    try:
        with Scrapetwitter() as bot:
            bot.login()
            articles = bot.competition_search(time)
            user_replies_count = bot.user_replies()
            return user_replies_count
    except Exception as e:
        if 'in PATH' in str(e):
            print(
                "You are trying to run the bot from command line \n"
                "Please add to PATH your Selenium Drivers \n"
                "Windows: \n"
                "   set PATH=%PATH%;C:path-to-your-folder \n \n"
                "Linux: \n"
                "   PATH=$PATH:/path/toyour/folder/ \n"
            )
        else:
            raise

async def get_user_retweets(time) -> Dict[str, any]:
    """Get tweet user replies"""
    try:
        with Scrapetwitter() as bot:
            bot.login()
            articles = bot.competition_search(time)
            user_retweets_count = bot.user_retweets()
            return user_user_retweets
    except Exception as e:
        if 'in PATH' in str(e):
            print(
                "You are trying to run the bot from command line \n"
                "Please add to PATH your Selenium Drivers \n"
                "Windows: \n"
                "   set PATH=%PATH%;C:path-to-your-folder \n \n"
                "Linux: \n"
                "   PATH=$PATH:/path/toyour/folder/ \n"
            )
        else:
            raise

async def get_user_likes(time) -> Dict[str, any]:
    """Get tweet user likes"""
    try:
        with Scrapetwitter() as bot:
            bot.login()
            articles = bot.competition_search(time)
            user_likes_count = bot.user_likes()
            return user_user_likes
    except Exception as e:
        if 'in PATH' in str(e):
            print(
                "You are trying to run the bot from command line \n"
                "Please add to PATH your Selenium Drivers \n"
                "Windows: \n"
                "   set PATH=%PATH%;C:path-to-your-folder \n \n"
                "Linux: \n"
                "   PATH=$PATH:/path/toyour/folder/ \n"
            )
        else:
            raise

async def leaderboard(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get tweet user likes"""
    job = context.job
    functions = [get_user_replies, get_user_retweets, get_user_likes]
    results = {}

    for func in functions:
        result = await func(job.data)

        while not isinstance(result, Dict):
            result = await func(job.data)

        results[func.__name__] = result

    replies_count = results["get_user_replies"]
    print(replies_count)
    likes_count = results["get_user_likes"]
    print(likes_count)
    retweet_count = results["get_user_retweets"]
    print(retweet_count)

    # Combine the dictionaries
    combined_counts = {}
    for username, count in replies_count.items():
        combined_counts.setdefault(username, {}).update({'replies': count})

    for username, count in likes_count.items():
        combined_counts.setdefault(username, {}).update({'likes': count})

    for username, count in retweet_count.items():
        combined_counts.setdefault(username, {}).update({'retweets': count})

    cursor = sqlite_conn.cursor

    # Execute a query to fetch data from the table
    cursor.execute("SELECT COUNT(*) FROM leaderboard")
    result = cursor.fetchone()

    # Check if the table is empty
    if result[0] == 0:
        # Iterate over the combined counts and insert them into the table
        for username, counts in combined_counts.items():
            replies = counts.get('replies', 0)
            likes = counts.get('likes', 0)
            retweets = counts.get('retweets', 0)
            total = replies + likes + retweets
            cursor.execute('INSERT INTO leaderboard VALUES (?, ?, ?, ?, ?)',
                           (username, replies, likes, retweets, total))
            sqlite_conn.commit()
    else:
        # Table is not empty, remove current data and add new ones
        cursor.execute("DELETE FROM leaderboard")
        # Perform your insert operation here
        for username, counts in combined_counts.items():
            replies = counts.get('replies', 0)
            likes = counts.get('likes', 0)
            retweets = counts.get('retweets', 0)
            total = replies + likes + retweets
            cursor.execute('INSERT INTO leaderboard VALUES (?, ?, ?, ?, ?)',
                           (username, replies, likes, retweets, total))
            sqlite_conn.commit()

async def send_tweets(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    cursor = sqlite_conn.cursor()
    cursor.execute(
        """
        SELECT * FROM `tweets` WHERE sent = ? ORDER BY id DESC LIMIT 1
        """,
        (False,),
    )

    rows = cursor.fetchone()

    if not rows:
        return
    elif rows['images'] != "":
        # if rows['videos'] != "":
        #     video_url = rows['videos']
        #     tweet_text = rows['tweets']
        #     # Download the video from the blob URL
        #     response = requests.get(video_url, stream=True)
        #     if response.status_code == 200:
        #         with open('video.mp4', 'wb') as video_file:
        #             response.raw.decode_content = True
        #             shutil.copyfileobj(response.raw, video_file)
        #
        #     # Send the video and tweet text together in a single Telegram message
        #     with open('video.mp4', 'rb') as video_file:
        #         await context.bot.send_video(job.chat_id, video=video_file, caption=tweet_text)

        image_url = rows['images']
        tweet_text = rows['tweets']
        await context.bot.send_photo(job.chat_id, photo=image_url, caption=tweet_text)

    else:
        text = f"\n{rows['tweets']}"
        await context.bot.send_message(job.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )
    cursor.execute(
        """
        UPDATE tweets SET sent=? WHERE id=?;
        """,
        (True, rows['id']),
    )
