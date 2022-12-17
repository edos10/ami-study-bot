from typing import Optional, Union
from telegram import (
    KeyboardButton,
    KeyboardButtonPollType,
    Poll,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    ForceReply
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ConversationHandler, ContextTypes
import sqlite3 as sql


async def gen_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    keyboard = [
        [
            InlineKeyboardButton("Дефолтные", callback_data="Стандарт"),
            InlineKeyboardButton("От пользователей", callback_data="Пользователи"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери, какие задачи хочешь решать", reply_markup=reply_markup)
    return 'choose_cluster'


async def choose_tasks_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if update.callback_query.data == "Стандарт":
        keyboard = [
            [
                InlineKeyboardButton("Матанализ", callback_data="Матанализ"),
                InlineKeyboardButton("Дискретная математика", callback_data="Дискретная математика"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text("Выбери предмет, по которому хочешь решать задачи:",
                                        reply_markup=reply_markup)
        return 'choose_subject'
    elif update.callback_query.data == "Пользователи":
        await update.callback_query.message.reply_text("Укажи коллекцию, из которой хочешь решать задачи:",
                                        reply_markup=ForceReply())
        return 'choose_collection'


async def choose_standard_task_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query = update.callback_query
    if query.data == "Матанализ":
        context.user_data["group"] = "matan_default"
    elif query.data == "Дискретная математика":
        context.user_data["group"] = "discr_default"
    context.user_data["text_group"] = False
    context.user_data["query_group"] = True
    return await send_task_message(update, context)


async def choose_task_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[int, str, None]:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(
        f"""SELECT * FROM All_Tasks WHERE GROUP_ID = "{update.message.text}" ORDER BY RANDOM() LIMIT 1;""")
    res = query_db.fetchone()
    conn.commit()
    conn.close()
    if res is None:
        await context.bot.sendMessage(
            text="Упс! Такой группы не существует. Создайте ее, если хотите!", chat_id=update.message.chat_id)
        context.user_data.clear()
        await context.bot.sendMessage(
            text="Заканчиваем подбор задач.", chat_id=update.message.chat_id)
        return ConversationHandler.END
    else:
        context.user_data["group"] = update.message.text
        context.user_data["text_group"] = True
        context.user_data["query_group"] = False
        return await send_task_message(update, context)


async def send_task_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute(f"""SELECT * FROM ALL_TASKS WHERE GROUP_ID = "{context.user_data["group"]}" ORDER BY RANDOM() LIMIT 1;""")
    res = query_db.fetchone()
    conn.commit()
    conn.close()
    if not context.user_data["text_group"] and context.user_data["query_group"]:
        await context.bot.send_message(text="Задача:", chat_id=update.callback_query.message.chat_id)
        context.user_data["task_number"] = res[0]
        if type(res[1]) == str:  # проверка на то, что перед нами, - фото или текст
            await context.bot.send_message(
                text=f"{res[1]}",
                chat_id=update.callback_query.message.chat_id)
        elif type(res[1]) == bytes:
            await context.bot.send_photo(
                photo=res[1],
                chat_id=update.callback_query.message.chat_id)
        await context.bot.send_message(text="Введите ваш ответ:",
                                       chat_id=update.callback_query.message.chat_id,
                                       reply_markup=ForceReply())
        return 'check_ans'
    elif context.user_data["text_group"] and not context.user_data["query_group"]:
        await context.bot.send_message(text="Задача:", chat_id=update.message.chat_id)
        context.user_data["task_number"] = res[0]
        if type(res[1]) == str:  # проверка на то, что перед нами, - фото или текст
            await context.bot.send_message(
                text=f"{res[1]}",
                chat_id=update.message.chat_id)
        elif type(res[1]) == bytes:
            await context.bot.send_photo(
                photo=res[1],
                chat_id=update.message.chat_id)
        await context.bot.send_message(text="Введите ваш ответ:",
                                       chat_id=update.message.chat_id,
                                       reply_markup=ForceReply())
        return 'check_ans'


async def get_all_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.split()
    if len(message) == 1:
        await context.bot.sendMessage(text="Команда должна быть задана в формате /all_tasks [название группы]",
                                      chat_id=update.message.chat_id)
    elif len(message) == 2:
        conn = sql.connect('database/study_bot.db')
        query_db = conn.cursor()
        query_db.execute(
            f"""SELECT * FROM All_Tasks WHERE GROUP_ID = "{message[1]}";""")
        res = query_db.fetchall()
        if res is None:
            await context.bot.sendMessage(
                text="Такой группы не существует, создайте ее, если хотите!", chat_id=update.message.chat_id)
            return
        for i in range(len(res)):
            answer = res[i][2]
            solution = res[i][3]
            task = res[i][1]
            if type(task) != str:
                await context.bot.send_photo(photo=task, chat_id=update.message.chat_id)
                task = 'Изображение выше'
            if type(answer) != str:
                await context.bot.send_photo(photo=answer, chat_id=update.message.chat_id)
                answer = 'Изображение выше'
            if type(solution) != str:
                await context.bot.send_photo(photo=solution, chat_id=update.message.chat_id)
                solution = 'Изображение выше'
            ans = str(i + 1) + '. ' + task + '\n Ответ: ' + answer + '\n Решение: ' + solution + '\n'
            await context.bot.send_message(
                text=f"{ans}",
                chat_id=update.message.chat_id)
        return 'check_ans'
    else:
        await context.bot.sendMessage(
            text="Команда невалидна, пожалуйста, введите аргументы еще раз!", chat_id=update.message.chat_id)
