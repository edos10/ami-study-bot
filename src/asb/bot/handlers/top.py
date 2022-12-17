import sqlite3 as sql
from os import mkdir
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from collections import deque

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute("""SELECT * FROM Students ORDER BY SUCCESS_SOLVE DESC LIMIT 10""")
    res = query_db.fetchall()
    text_top = ''
    iter = min(10, len(res))
    for i in range(iter):
        text_top += str(i + 1) + ". "
        if res[i][1] is not None:
            text_top += res[i][1]
        if res[i][2] is not None:
            text_top += " " + res[i][2]
        text_top += f", решено задач: {res[i][3]}\n"
    await context.bot.send_message(text=text_top, chat_id=update.message.chat_id)