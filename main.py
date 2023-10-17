import asyncio
import telebot
from MyToken import TOKEN
from utils.Logger import Logger, MiddlewareLogger, logging
from utils.handlers.database_handler import DatabaseHandler
from utils.handlers.message_handler import StateMachine, MessageHandler
from bot_logic.state_graph import state_graph


logger = Logger('bot.log')
bot = telebot.TeleBot(TOKEN)

database_handler = MiddlewareLogger(
                target_class=DatabaseHandler('sqlite:///SQLiteBotDB.db'),
                log_prefix='Request to db',
                logger=logger,
                debug=True,
                excluded_methods=['Session']
                )

choice_machine = StateMachine(state_graph)
message_handler = MessageHandler(choice_machine, bot, database_handler)


@bot.message_handler(content_types=['text'])
def handle_incoming_message(message):
    user_info = f"{message.from_user.first_name} {message.from_user.last_name}"
    message_text = message.text
    log_message = f"Chat ID: {message.chat.id} | User: {user_info} | Message text: {message_text}"
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


# if you have got error with lib "pytube" version (15.0.0), fallow this change
# venv/lib/python3.10/site-packages/pytube/cipher.py - line 411
#  old: transform_plan_raw = find_object_from_startpoint(raw_code, match.span()[1] - 1)
#  new: transform_plan_raw = js
#
# venv/lib/python3.10/site-packages/pytube/parser.py - line 159
# old: func_regex = re.compile(r"function\([^)]*\)") - probably bugs
# new: func_regex = re.compile(r"function\([^)]?\)")
#
# venv/lib/python3.10/site-packages/pytube/innertube.py - line 223
# old: def __init__(self, client='ANDROID_MUSIC', use_oauth=False, allow_cache=True):
# new: def __init__(self, client='WEB', use_oauth=False, allow_cache=True):