from typing import Optional
import sqlite3 as sql
from telegram import Chat, ChatMember, User, ChatMemberUpdated, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Проверяем, есть ли пользователь в Teachers
    conn = sql.connect('database/study_bot.db')
    query_db = conn.cursor()
    if update.callback_query is not None:
        query_db.execute("""SELECT * from Teachers WHERE ID = {}""".format(update.callback_query.from_user.id))
    else:
        query_db.execute("""SELECT * from Teachers WHERE ID = {}""".format(update.message.from_user.id))
    response = query_db.fetchall()
    conn.commit()
    conn.close()
    if len(response) > 0:  # Значит, пользователь в Teachers
        text = """Вы - преподаватель. Ваши команды:.\n1) /add - добавить в коллекцию карточку\n
        2) /gen_work (TODO) - сгенерировать тест\n4) /stats (TODO) - посмотреть статистику учеников\n"""  # <------- дописать, если будет что-то ещё

        if update.callback_query is not None:
            await context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=text)
        else:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=text)
    else:
        text = """Вы - студент. Ваши команды:\n
1) /add - добавить в коллекцию карточку.\n
2) /gen_task - решить рандомную задачу по мат. анализу или дискретной математике из существующих.\n
3) /gen_task [название группы] - решить рандомную задачу из группы.\n
4) /top - посмотреть топ-10 людей, решивших больше всех задач.\n"""

        if update.callback_query is not None:
            await context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=text)
        else:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=text)
