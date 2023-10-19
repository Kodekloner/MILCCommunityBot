<p align="center">
    <img src="logo/milclogo.jpg" style="background: white; border-radius: 10%; padding: 10px" alt="Logo" width="200px">
</p>


<p align="center">
   <a href="https://t.me/milc_community_bot"><img alt="Telegram Link" src="https://img.shields.io/badge/Telegram-%40milc_community_bot-blue"></a>
</p>

<h2 align="center">MILC Community Bot</h2>
<p align="center">A modular, asynchronous, highly-configurable, plug and play Telegram bot built using the fantastic <a href="https://github.com/python-telegram-bot/python-telegram-bot"><code>python-telegram-bot</code></a> library.</p>

## Introduction

## ✨ Features

## 🏗 Usage

### Configuration

Before you can begin, you'll need to get a token and API keys for your bot. You can get the token from [@BotFather](https://t.me/botfather).

Run the following command to generate an empty environment file:

```bash
$ git clone https://github.com/Kodekloner/MILCCommunityBot.git
$ cd MILCCommunityBot
$ pip install -r requirements.txt
$ cp .env.example .env
```

2. Now fill up the `.env` file with all the API keys you need. The only mandatory key is the Telegram bot token.

### Running

To start the bot you only need the valid `.env` file.

```bash
$ python main.py
```

## Recommended Reading

- [Telegram API documentation](https://core.telegram.org/bots/api)
- [`python-telegram-bot` documentation](https://python-telegram-bot.readthedocs.io/)
