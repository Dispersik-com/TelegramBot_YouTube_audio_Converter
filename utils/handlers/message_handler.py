import copy
from utils.handlers.command_handler import CommandHandler
from utils.handlers.handle_markup import handle_markup
from bot_communication_logic.report_messages import Languages


class MessageHandler:
    """
   Class for handling user messages and executing appropriate commands.
   Responsible for processing user messages, managing user state, and executing commands.
   """
    def __init__(self, state_machine, bot, database_handler):
        """
        Initialize the MessageHandler.

        :param state_machine: An instance of StateMachine for handling message states.
        :param bot: The Telegram bot instance.
        :param database_handler: An instance of DatabaseHandler for database operations.
        """
        self.state_machine = state_machine
        self.bot = bot
        self.database_handler = database_handler
        self.command_handler = CommandHandler(bot, database_handler)

    async def handle_message(self, message):
        """
        Handle incoming messages.

        :param message: Incoming message from the user.
        """
        session = self.database_handler.Session()

        user = self.database_handler.get_user_by_chat_id(session, message.chat.id)

        if not user:
            user = self.database_handler.add_user(session,
                                                  message.chat.id,
                                                  message.from_user.first_name,
                                                  message.from_user.last_name,
                                                  state='/start')

        if user.language is None or message.text == 'Select language':
            handle_markup(self.bot, message.chat.id,
                          'Please, select language', Languages)
            await self.handle_command('select_language', user)
            session.close()
            return

        state = self.state_machine.get_state(message.text, language=user.language)

        if state is not None:
            command = state.get('command')
            text = state.get('text')
            options = state.get('options')

            handle_markup(self.bot, user.chat_id, text, options)

            updated_user = self.database_handler.update_state(session, user.id, state.get('state_name'))
            print('previous_state ', user.previous_state, ' --> ', state.get('state_name'))
            await self.handle_command(command, updated_user)
        else:
            self.handle_unknown_message(message)

        session.close()

    async def handle_command(self, command_name, user):
        """
        Handle commands based on the provided command name.

        :param command_name: Name of the command to handle.
        :param user: User object associated with the message.

        :return: None.
        """
        if hasattr(self.command_handler, f"handle_{command_name}"):
            command_name = getattr(self.command_handler, f"handle_{command_name}")
            user = copy.copy(user)
            command_name(user)

    def handle_unknown_message(self, message):
        """
        Handle unknown or invalid commands by sending a warning message.

        :param message: Incoming message.

        :return: None.
        """
        warning_text = "Unknown or incorrect command. Please choose from the available commands."
        self.bot.send_message(message.chat.id, text=warning_text)
