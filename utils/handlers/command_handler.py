from utils.handlers.command_helper.sub_command import *
from utils.handlers.command_helper.next_steps import NextStepHandler
import functools


def register_next_step(next_step_handler):
    def decorator(handler_func):
        @functools.wraps(handler_func)
        def wrapper(self, user):
            chat_id = user.chat_id

            if next_step_handler:
                self.bot.register_next_step_handler_by_chat_id(int(chat_id),
                                                               next_step_handler,
                                                               self.bot,
                                                               self.db,
                                                               user)
            else:
                raise ValueError(f"No matching next step handler for {handler_func.__name__}")

        return wrapper
    return decorator


class CommandHandler:
    """
    The CommandHandler class is designed for executing commands,
    and it encapsulates functions that start with the "handle_" prefix.
    All functions within the class expect one argument,
    which is a copy of the User object, and are used for executing the corresponding command.
    """

    def __init__(self, bot, database_handler):
        """
        Initialize the CommandHandler.

        :param bot: The Telegram bot instance.
        :param database_handler: An instance of DatabaseHandler for database operations.
        """
        self.bot = bot
        self.db = database_handler

    def handle_download(self, user):
        chat_id = user.chat_id
        language = user.language

        downloader = YoutubeDownloader(user.url, f'{chat_id}_videos')
        local_video_file_name = downloader.download()

        if os.path.exists(local_video_file_name):
            converter = VideoConverter(local_video_file_name, f'{chat_id}_audios')
            local_audio_file_name = converter.convert_to_audio('mp3')

            if os.path.exists(local_audio_file_name):
                with open(local_audio_file_name, 'rb') as audio:
                    self.bot.send_audio(chat_id, audio)

                converter.clean_output_folder()

            downloader.clean_output_folder()

            return

        self.bot.send_message(chat_id, report_text[language]["error"])

    def handle_download_all(self, user):
        multiple_download(user, self.db, self.bot)

    def handle_download_selected(self, user):
        selected_songs = get_selected_songs_by_user(user, self.db)
        multiple_download(user, self.db, self.bot, only_selected_songs=selected_songs)

    # command with next step
    @register_next_step(NextStepHandler.wait_select_language)
    def handle_select_language(self, user):
        pass

    @register_next_step(NextStepHandler.wait_url_song)
    def handle_wait_url_from_song(self, user):
        pass

    @register_next_step(NextStepHandler.wait_url_video_with_timestamps)
    def handle_wait_url_video_with_timestamps(self, user):
        pass

    @register_next_step(NextStepHandler.wait_timecodes)
    def handle_set_timecodes(self, user):
        pass

    @register_next_step(NextStepHandler.wait_select_songs)
    def handle_select_songs(self, user):
        pass
