import logging
from environs import Env
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Updater,
    Filters,
)
from handlers import (
    AWAIT_AGREEMENT,
    AWAIT_NAME,
    AWAIT_PHONE,
    AWAIT_MENU_CHOICE,
    AWAIT_RECIPE_ACTION,
    AWAIT_FAVORITES_ACTION,
    FINISH,
    start,
    handle_agreement,
    handle_name,
    handle_phone,
    show_menu,
    show_recipe,
    show_favorites
)

logger = logging.getLogger(__name__)


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    updater = Updater(env('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AWAIT_AGREEMENT: [
                CallbackQueryHandler(handle_agreement, pattern='agree$'),
            ],
            AWAIT_NAME: [
                MessageHandler(Filters.text & ~Filters.command, handle_name),
            ],
            AWAIT_PHONE: [
                MessageHandler(Filters.text & ~Filters.command, handle_phone),
            ],
            AWAIT_MENU_CHOICE: [
                CallbackQueryHandler(show_recipe, pattern='^recipe$'),
                CallbackQueryHandler(show_favorites, pattern='^favorites$'),
            ],
            AWAIT_RECIPE_ACTION: [
                CallbackQueryHandler(show_menu, pattern='^menu$'),
                CallbackQueryHandler(show_recipe, pattern='^like'),
                CallbackQueryHandler(show_recipe, pattern='^dislike'),
            ],
            AWAIT_FAVORITES_ACTION: [
                CallbackQueryHandler(show_menu, pattern='^menu$'),
                CallbackQueryHandler(show_favorites, pattern='^page'),
                CallbackQueryHandler(show_recipe, pattern='^recipe'),
            ],
            FINISH: [
                CallbackQueryHandler(start, pattern='^start$')
            ]
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
