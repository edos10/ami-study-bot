### External Modules
import logging
from telegram.ext import (
    filters,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

### Internal Modules
# bot config
from .load_config import BotConfig

# handlers
from .handlers.start import *
from .handlers.help import *
from .handlers.add import *
from .handlers.gen_tasks import *
from .handlers.check_ans import *
from .handlers.top import *


def run_bot(config_file_path: str):
    # get bot configuration
    bot_config: BotConfig = BotConfig.from_file(config_file_path)

    # build the bot application using bot token
    application = ApplicationBuilder().token(bot_config.token).build()

    # add handlers
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={'choose_role': [CallbackQueryHandler(choose_role)]},
        fallbacks=[]
    )

    help_handler = CommandHandler('help', bot_help)
    my_stat_handler = CommandHandler('my_stat', my_stat)
    all_tasks_handler = CommandHandler('all_tasks', get_all_tasks)
    top_handler = CommandHandler('top', top)

    add_task_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_task)],
        states={'prep_task': [MessageHandler(filters=(filters.TEXT | filters.PHOTO), callback=prep_task)],
                'prep_ans': [MessageHandler(filters=filters.TEXT, callback=prep_ans)],
                'prep_solution': [MessageHandler(filters=(filters.TEXT | filters.PHOTO), callback=prep_solution)],
                'prep_collection': [MessageHandler(filters=filters.TEXT, callback=prep_collection)],
                'create_collection': [CallbackQueryHandler(create_collection)]},
        fallbacks=[]
    )

    solve_handler = ConversationHandler(
        entry_points=[CommandHandler('gen_task', gen_task)],
        states={
            'choose_cluster': [CallbackQueryHandler(choose_tasks_cluster)],
            'choose_subject': [CallbackQueryHandler(choose_standard_task_group)],
            'choose_collection': [MessageHandler(filters.TEXT, choose_task_collection)],
            'check_ans': [MessageHandler(filters.TEXT, check_ans)],
            'choose_next_when_correct': [CallbackQueryHandler(choose_next_step_correct)],
            'choose_next_when_incorrect': [CallbackQueryHandler(choose_next_step_incorrect)]
        },
        fallbacks=[]
    )

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(add_task_handler)
    application.add_handler(solve_handler)
    application.add_handler(my_stat_handler)
    application.add_handler(all_tasks_handler)
    application.add_handler(top_handler)

    # initialize and start the bot application
    application.run_polling()
