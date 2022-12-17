from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes
import sqlite3 as sql


async def gen_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.split()
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM Teachers WHERE ID = "{update.message.from_user.id}";""")
    res = query_db.fetchone()
    if res is None:
        await context.bot.sendMessage(
            text="Вы не преподаватель, поэтому не можете генерировать работу, пожалуйста, воспользуйтесь другой опцией.",
            chat_id=update.message.chat_id)
        return
    if len(message) == 1:
        await context.bot.sendMessage(text="Вы не написали номер группы, поэтому выберите, какие задачи из общего списка вы бы хотели сгенерировать.!",
                                      chat_id=update.message.chat_id)
        """Sends a message with three inline buttons attached."""
        keyboard = [
            [
                InlineKeyboardButton("Матанализ", callback_data="Матанализ"),
                InlineKeyboardButton("Дискретная математика", callback_data="Дискретная математика"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Выберите предмет, по которому вы хотите решить задачу:", reply_markup=reply_markup)
    elif len(message) == 2:
        conn = sql.connect('database/study_bot.db')
        query_db = conn.cursor()
        query_db.execute(
            f"""SELECT * FROM All_Tasks WHERE GROUP_ID = "{message[1]}" ORDER BY RANDOM() LIMIT 1;""")
        res = query_db.fetchone()
        print(res)
        if res is None:
            await context.bot.sendMessage(
                text="Такой группы не существует, создайте ее, если хотите!", chat_id=update.message.chat_id)
            return
        await context.bot.send_message(
            text=f"{res[1]}",
            chat_id=update.message.chat_id)
    else:
        await context.bot.sendMessage(
            text="Команда невалидна, пожалуйста, введите аргументы еще раз!", chat_id=update.message.chat_id)

gen_work_handler = CommandHandler("gen_work", gen_work)
