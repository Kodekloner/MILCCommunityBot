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

# query = f"DROP TABLE IF EXISTS user_wallet_twitter"
query = "ALTER TABLE user_wallet_twitter ADD COLUMN first_name TEXT;"
cursor.execute(query)

# Chat Statistics Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chat_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL,
        title TEXT,
        type TEXT
    )
    """
)

# Chat Statistics Table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usersame TEXT,
        address TEXT,
        total INTEGER,
        amount FLOAT(8),
        status TEXT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `TwitterSearch`(
        `id` INTEGER PRIMARY KEY,
        `word` TEXT,
        `since_id` INTEGER
    );
    """
)

# Table for Tweets
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `tweets` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `tweets` TEXT NOT NULL,
        `tw_id` INTEGER,
        `images` TEXT,
        `created_at` TEXT,
        `username` TEXT,
        `sent_at` TEXT,
        `sent` BOOLEAN
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `leaderboard` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `username` TEXT,
        `tweets` INTEGER,
        `replies` INTEGER,
        `likes` INTEGER,
        `retweets` INTEGER,
        `quotes` INTEGER,
        `total` INTEGER
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `leaderboard_time_intervals` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `time_intervals` TEXT
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `point_system` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `tweets` INTEGER,
        `replies` INTEGER,
        `likes` INTEGER,
        `retweets` INTEGER,
        `quotes` INTEGER
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `prize` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `token` FLOAT(8)
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `user_wallet_twitter` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `userid` TEXT,
        `twitter_username` TEXT,
        `address` TEXT,
        `chat_id` TEXT,
        `username` TEXT,
        `telegram_group` TEXT,
        `ban` BOOLEAN,
        `first_name` TEXT
    );
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS `admin_wallet` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `address` TEXT,
        `private_key` TEXT,
        `mnemonic` TEXT,
        `balance` TEXT
    );
    """
)
