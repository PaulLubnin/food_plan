import logging
from django.core.management.base import BaseCommand
from environs import Env
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Updater,
    Filters,
)

from recipes.bot_handlers import (
    AWAIT_AGREEMENT, AWAIT_NAME, AWAIT_PHONE, AWAIT_MENU_CHOICE, AWAIT_CATEGORY_CHOICE, AWAIT_RECIPE_ACTION,
    AWAIT_FAVORITES_ACTION, FINISH, start, handle_agreement, handle_name, handle_phone, handle_recipe_action,
    show_categories, show_recipe, show_favorites, return_to_menu, return_to_menu_from_favorites
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запуск чат-бота'

    def handle(self, *args, **options):
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
                    CallbackQueryHandler(show_recipe, pattern='^recipe$'),
                    CallbackQueryHandler(show_categories, pattern='^categories$'),
                    CallbackQueryHandler(show_favorites, pattern='^favorites$'),
                ],
                AWAIT_CATEGORY_CHOICE: [
                    CallbackQueryHandler(show_recipe, pattern='^category'),
                ],
                AWAIT_RECIPE_ACTION: [
                    CallbackQueryHandler(show_recipe, pattern='^recipe$'),
                    CallbackQueryHandler(return_to_menu, pattern='^menu$'),
                    CallbackQueryHandler(handle_recipe_action, pattern=r'\w*like-\d+'),
                ],
                AWAIT_FAVORITES_ACTION: [
                    CallbackQueryHandler(return_to_menu_from_favorites, pattern='^menu$'),
                    CallbackQueryHandler(show_recipe, pattern='^recipe'),
                    CallbackQueryHandler(show_favorites, pattern='^page'),
                ],
                FINISH: [
                    CommandHandler('start', start)
                ]
            },
            fallbacks=[CommandHandler('start', start)],
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()
