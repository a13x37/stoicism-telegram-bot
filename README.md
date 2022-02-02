# Stoicism Telegram Bot
A simple bot with some set of quotes from Stoic philosophers.  
Also, you can subscribe for daily inspiration. Phrases will be coming at 10 a.m GMT+3.

Bot built with Telegram Bot API (receiving incoming updates through an outgoing webhook).  
Interaction with the database through the adapter psycopg2, queries are written in SQL.  
List of articles (and links) parsed with BeautifulSoup.  
Deployed on Heroku.


## Functionalities
- Receive a random quote by request
- Subscription to daily quote
- Short description of philosophy, several articles

## Available languages 
Russian is available  
English is coming soon


# Variables
- `BOT_TOKEN`   Your bot token from @BotFather
- `APP_URL`     Your WebHook URL
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` Database credentials

The project was created to learn Flask, PostgreSQL, Telegram API, etc.
Used content by [Jegor Nagel](https://jegornagel.com/)