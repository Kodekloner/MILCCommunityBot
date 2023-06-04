import os
import sqlite3


def is_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )


sqlite_conn = sqlite3.connect(
    f"{os.getcwd() if not is_docker() else '/db'}/MICL.db",
    check_same_thread=False,
    isolation_level=None,
)

sqlite_conn.row_factory = sqlite3.Row

cursor = sqlite_conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `TwitterSearch`(
        `id` INTEGER PRIMARY KEY,
        `word` TEXT NOT NULL,
        `time` TIMESTAMP NOT NULL
    );
    """
)

# Table for Tweets
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `tweets` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `tweets` TEXT NOT NULL,
        `images` TEXT,
        `sent` BOOLEAN
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `leaderboard` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `username` TEXT,
        `replies` INTEGER,
        `likes` INTEGER,
        `retweets` INTEGER,
        `total` INTEGER
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `user_wallet_twitter` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `userid` TEXT,
        `twitter_username` TEXT,
        `address` TEXT
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `admin_wallet` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `address` TEXT,
        `private_key` TEXT,
        `mnemonic` TEXT
    );
    """
)
