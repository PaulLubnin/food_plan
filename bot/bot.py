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
    AWAIT_AGREEMENT, AWAIT_NAME, AWAIT_PHONE, AWAIT_MENU_CHOICE, AWAIT_RECIPE_ACTION, AWAIT_FAVORITES_ACTION,
    FINISH, start, handle_agreement, handle_name, handle_phone, handle_menu_choice, handle_recipe_action,
    handle_favorites_action
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
                CallbackQueryHandler(handle_agreement, pattern=r'\w*agree$'),
            ],
            AWAIT_NAME: [
                MessageHandler(Filters.text & ~Filters.command, handle_name),
            ],
            AWAIT_PHONE: [
                MessageHandler(Filters.text | Filters.contact & ~Filters.command, handle_phone),
            ],
            AWAIT_MENU_CHOICE: [
                CallbackQueryHandler(handle_recipe_action, pattern='^recipe$'),
                CallbackQueryHandler(handle_favorites_action, pattern='^favorites$'),
            ],
            AWAIT_RECIPE_ACTION: [
                CallbackQueryHandler(handle_menu_choice, pattern='^menu$'),
                CallbackQueryHandler(handle_recipe_action, pattern=r'\w*like$'),
            ],
            AWAIT_FAVORITES_ACTION: [
                CallbackQueryHandler(handle_menu_choice, pattern='^menu$'),
                CallbackQueryHandler(handle_favorites_action, pattern='^page'),
                CallbackQueryHandler(handle_recipe_action, pattern='^recipe'),
            ],
            FINISH: [
                CommandHandler('start', start)
            ]
        },
        fallbacks=[],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
