from typing import Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ConversationHandler, ContextTypes
import sqlite3 as sql
from .gen_tasks import send_task_message
from .help import bot_help


async def check_ans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user_id = update.message.from_user.id
    print(context.user_data)
    task_number = context.user_data["task_number"]
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM All_Tasks WHERE ID = "{task_number}";""")
    res = query_db.fetchone()
    ans = res[2]

    query_db.execute(
        f"""SELECT * FROM Students WHERE ID = "{user_id}";""")
    res = query_db.fetchone()
    attempts = res[4] + 1
    query_db.execute(
        f"""UPDATE Students set ALL_ATTEMPTS = {attempts} WHERE ID = "{user_id}";""")

    if ans == message:
        query_db.execute(
            f"""SELECT * FROM Students WHERE ID = "{user_id}";""")
        res = query_db.fetchone()
        success_solve = res[3] + 1
        query_db.execute(
            f"""UPDATE Students set SUCCESS_SOLVE = {success_solve} WHERE ID = "{user_id}";""")
        await context.bot.send_message(
            text=f"Правильно!",
            chat_id=update.message.chat_id)

        keyboard = [
            [
                InlineKeyboardButton("Ещё", callback_data="Новая задача"),
                InlineKeyboardButton("Выйти", callback_data="Выйти к списку команд"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
        conn.commit()
        conn.close()
        return 'choose_next_when_correct'
    else:
        await context.bot.send_message(
            text=f"Неправильно :(",
            chat_id=update.message.chat_id)

        keyboard = [
            [
                InlineKeyboardButton("Решение", callback_data="Посмотреть решение"),
                InlineKeyboardButton("Ещё", callback_data="Новая задача"),
                InlineKeyboardButton("Выйти", callback_data="Выйти к списку команд"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Что дальше?", reply_markup=reply_markup)
        conn.commit()
        conn.close()
        return 'choose_next_when_incorrect'


async def choose_next_step_correct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str]:
    query = update.callback_query
    if query.data == "Новая задача":
        context.user_data["text_group"] = False
        context.user_data["query_group"] = True
        return await send_task_message(update, context)
    elif query.data == "Выйти к списку команд":
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END


async def choose_next_step_incorrect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str, None]:
    query = update.callback_query
    if query.data == "Посмотреть решение":
        return await show_ans(update, context)
    elif query.data == "Новая задача":
        context.user_data["text_group"] = False
        context.user_data["query_group"] = True
        return await send_task_message(update, context)
    elif query.data == "Выйти к списку команд":
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END


async def show_ans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    task_number = context.user_data["task_number"]
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM All_Tasks WHERE ID = "{task_number}" ORDER BY RANDOM() LIMIT 1;""")
    res = query_db.fetchone()
    ans = res[2]
    await context.bot.send_message(
        text=f"Правильный ответ: {ans}",
        chat_id=update.callback_query.message.chat_id)

    keyboard = [
        [
            InlineKeyboardButton("Ещё", callback_data="Новая задача"),
            InlineKeyboardButton("Выйти", callback_data="Выйти к списку команд"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text("Что дальше?", reply_markup=reply_markup)
    return 'choose_next_when_incorrect'


async def my_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sql.connect('database/study_bot.db')
    user_id = update.message.from_user.id
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM Students WHERE ID = "{user_id}" ORDER BY RANDOM() LIMIT 1;""")
    res = query_db.fetchone()
    success_solve = res[3]
    attempts = res[4]
    await context.bot.send_message(
        text=f"Вы решили правильно: {success_solve} задач \n"
             f"Вы пробовали решить: {attempts} задач",
        chat_id=update.message.chat_id)
