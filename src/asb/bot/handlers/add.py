from typing import Optional, Union
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

from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from .help import bot_help


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    print(context.user_data)
    context.user_data["chat_id"] = update.message.chat_id
    await context.bot.send_message(text="Напишите в сообщения или пришлите фотографией условие вашей задачи:",
                                   chat_id=update.message.chat_id, reply_markup=ForceReply(input_field_placeholder="Задача"))
    return 'prep_task'


async def prep_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if len(update.message.photo) > 0:
        photo_id = update.message.photo[-1].file_id
        photo_file = await context.bot.get_file(photo_id)
        photo_bytes = await photo_file.download_as_bytearray()
        context.user_data["photo_task"] = photo_bytes
    else:
        context.user_data["text_task"] = update.message.text

    await context.bot.send_message(text="Напишите ответ к заданию:",
                                   chat_id=update.message.chat_id, reply_markup=ForceReply(input_field_placeholder="Ответ"))
    return 'prep_ans'


async def prep_ans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    context.user_data["ans"] = update.message.text

    await context.bot.send_message(text="Напишите в сообщения или пришлите фотографией решение:",
                                   chat_id=update.message.chat_id, reply_markup=ForceReply(input_field_placeholder="Решение"))
    return 'prep_solution'


async def prep_solution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if len(update.message.photo) > 0:
        photo_id = update.message.photo[-1].file_id
        photo_file = await context.bot.get_file(photo_id)
        photo_bytes = await photo_file.download_as_bytearray()
        context.user_data["photo_solution"] = photo_bytes
    else:
        context.user_data["text_solution"] = update.message.text
    await context.bot.send_message(text="Выберите или создайте коллекцию, в которую хотите что-то добавить. Для этого напишите ниже название коллекции:",
                                   chat_id=update.message.chat_id, reply_markup=ForceReply(input_field_placeholder="Коллекция"))
    return 'prep_collection'


async def prep_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Union[str, int]:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute("""SELECT GROUP_ID FROM ALL_TASKS""")
    response = set([group[0] for group in query_db.fetchall()])
    conn.commit()
    conn.close()
    if update.message.text not in response:
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data="Да"),
                InlineKeyboardButton("Нет", callback_data="Нет"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data["collection"] = update.message.text
        context.user_data["new_collection"] = True
        await context.bot.send_message(
            text="Такой коллекции пока нет. Мне её создать?",
            chat_id=update.message.chat_id, reply_markup=reply_markup)
        return 'create_collection'
    else:
        context.user_data["collection"] = update.message.text
        await add_query(update, context)
        await bot_help(update, context)
        return ConversationHandler.END


async def create_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query.data == "Да":
        await add_query(update, context)
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END
    elif update.callback_query.data == "Нет":
        await context.bot.send_message(
            text="Создание коллекции и задачи отменено",
            chat_id=context.user_data["chat_id"])
        context.user_data.clear()
        await bot_help(update, context)
        return ConversationHandler.END


async def add_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    query_db.execute("""SELECT max(ID) FROM ALL_TASKS;""")
    item_id = query_db.fetchone()[0] + 1
    if "text_task" in context.user_data:
        if "text_solution" in context.user_data:
            query_db.execute("""INSERT INTO ALL_TASKS VALUES(?, ?, ?, ?, ?);""",
                             (item_id, context.user_data["text_task"], context.user_data["ans"],
                              context.user_data["text_solution"], context.user_data["collection"]))
        else:
            query_db.execute("""INSERT INTO ALL_TASKS VALUES(?, ?, ?, ?, ?);""",
                             (item_id, context.user_data["text_task"], context.user_data["ans"],
                              context.user_data["photo_solution"], context.user_data["collection"]))
    else:
        if "text_solution" in context.user_data:
            query_db.execute("""INSERT INTO ALL_TASKS VALUES(?, ?, ?, ?, ?);""",
                             (item_id, context.user_data["photo_task"], context.user_data["ans"],
                              context.user_data["text_solution"], context.user_data["collection"]))
        else:
            query_db.execute("""INSERT INTO ALL_TASKS VALUES(?, ?, ?, ?, ?);""",
                             (item_id, context.user_data["photo_task"], context.user_data["ans"],
                              context.user_data["photo_solution"], context.user_data["collection"]))
    conn.commit()
    conn.close()

    if "new_collection" in context.user_data:
        await context.bot.send_message(text="Новая группа {} была добавлена.".format(context.user_data["collection"]), chat_id=context.user_data["chat_id"])
    await context.bot.send_message(text="Новая задача была добавлена в группу.", chat_id=context.user_data["chat_id"])
