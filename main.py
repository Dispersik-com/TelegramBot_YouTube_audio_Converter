import asyncio
import telebot
from MyToken import TOKEN
from utils.Logger import Logger, MiddlewareLogger, logging
from utils.handlers.database_handler import DatabaseHandler
from utils.handlers.message_handler import MessageHandler
from bot_communication_logic.state_graph import state_graph
from bot_communication_logic.state_machine import StateMachine


logger = Logger('bot.log')
bot = telebot.TeleBot(TOKEN)

database_handler = (MiddlewareLogger(
                target_class=DatabaseHandler('sqlite:///SQLiteBotDB.db'),
                log_prefix='Request to db',
                logger=logger,
                debug=False,
                excluded_methods=['Session', 'close']
                )
                .add_format_argument_func('Session', lambda x: f"Session_hash: {hash(x)}"))

choice_machine = StateMachine(state_graph)
message_handler = MessageHandler(choice_machine, bot, database_handler)


@bot.message_handler(content_types=['text'])
def handle_incoming_message(message):
    user_info = f"{message.from_user.first_name} {message.from_user.last_name}"
    message_text = message.text
    log_message = (f"Chat ID: {message.chat.id} |"
                   f" User: {user_info} |"
                   f" Message text: {message_text}")
    logging.info("Received message -- " + log_message)
    asyncio.run(message_handler.handle_message(message))


if __name__ == '__main__':
    try:
        logging.info('-- Bot started --')
        bot.infinity_polling()
    except Exception as e:
        raise e
    finally:
        database_handler.close()