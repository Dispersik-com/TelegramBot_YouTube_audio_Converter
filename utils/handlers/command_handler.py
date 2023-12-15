import os
import re

from utils.media_tools import YoutubeDownloader, VideoConverter, is_youtube_url
from utils.handlers.handle_markup import handle_markup
from bot_logic.report_messages import report_text, Languages


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

    def handle_select_language(self, user):
        chat_id = user.chat_id

        self.bot.register_next_step_handler_by_chat_id(int(chat_id),
                                                       NextStepHandler.wait_select_language,
                                                       self.bot,
                                                       self.db,
                                                       user)

    def handle_wait_url_from_song(self, user):
        chat_id = user.chat_id

        self.bot.register_next_step_handler_by_chat_id(int(chat_id),
                                                       NextStepHandler.wait_url_song,
                                                       self.bot,
                                                       self.db,
                                                       user)

    def handle_wait_url_video_with_timestamps(self, user):
        chat_id = user.chat_id

        self.bot.register_next_step_handler_by_chat_id(int(chat_id),
                                                       NextStepHandler.wait_url_video_with_timestamps,
                                                       self.bot,
                                                       self.db,
                                                       user)

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
        SubCommand.multiple_download(user, self.db, self.bot)

    def handle_select_songs(self, user):
        chat_id = user.chat_id

        self.bot.register_next_step_handler_by_chat_id(int(chat_id),
                                                       NextStepHandler.wait_select_songs,
                                                       self.bot,
                                                       self.db,
                                                       user)

    def handle_set_timecodes(self, user):
        chat_id = user.chat_id

        self.bot.register_next_step_handler_by_chat_id(int(chat_id),
                                                       NextStepHandler.wait_timecodes,
                                                       self.bot,
                                                       self.db,
                                                       user)

    def handle_download_selected(self, user):
        selected_songs = SubCommand.get_selected_songs_by_user(user, self.db)
        SubCommand.multiple_download(user, self.db, self.bot, only_selected_songs=selected_songs)


class NextStepHandler:
    """
        A class that encapsulates functions to be executed on the next step of a command.
    """

    @staticmethod
    def decorator_wait_url(func):
        def wrapper(*args, **kwargs):
            message, bot, db, user = args
            language = user.language
            chat_id = user.chat_id
            if is_youtube_url(message.text):
                url = message.text

                func(*args, **kwargs)

                if SubCommand.save_url(db, user, url) is not True:
                    bot.send_message(chat_id, report_text[language]["error"])
            else:
                bot.send_message(user.chat_id, report_text[language]["invalid_link"])
                # handle_markup(bot, int(user.chat_id), '', [''])
            return
        return wrapper

    @staticmethod
    @decorator_wait_url
    def wait_url_song(url, bot, db, user):
        pass

    @staticmethod
    @decorator_wait_url
    def wait_url_video_with_timestamps(url, bot, db, user):
        language = user.language
        tracklist = SubCommand.find_songs_in_description(url)
        if tracklist is None:
            bot.send_message(user.chat_id, report_text[language]["not_found"])

        if SubCommand.save_tracklist(db, user, tracklist):
            tracklist_text = f"Found songs: \n\n{SubCommand.format_tracklist_to_text(tracklist)}"
            bot.send_message(user.chat_id, tracklist_text)
        else:
            bot.send_message(user.chat_id, report_text[language]["error"])
            # handle_markup(bot, user.chat_id, text, ["Download Selected", "Start over"])

    @staticmethod
    def wait_select_language(message, bot, db, user):
        chat_id = int(user.chat_id)
        language = "EN"
        if message.text in Languages:
            session = db.Session()
            if db.set_user_language(session, user.id, message.text):
                handle_markup(bot, chat_id, report_text[message.text]['successfully'], ['/start'])
            else:
                bot.send_message(chat_id, report_text[language]['error'])
            session.close()
            return
        else:
            handle_markup(bot, chat_id, report_text[language]['not_found_language'], ['Select language'])

    @staticmethod
    def wait_select_songs(message, bot, db, user):
        chat_id = int(user.chat_id)
        language = user.language

        selected_song_indices = list(map(int, re.findall(r'\d+', message.text)))

        if selected_song_indices:
            session = db.Session()
            db.set_selected_songs(session, user.id, selected_song_indices)
            songs = db.get_songs(session, user.id)
            session.close()

            selected_songs = list(filter(lambda x: songs.index(x) + 1 in selected_song_indices, songs))

            report = (report_text[language]["info_selected"] +
                      SubCommand.format_tracklist_to_text(selected_songs))

            handle_markup(bot, chat_id, report, ["Download Selected", "Start over"])
        else:
            bot.send_message(chat_id, report_text[language]["not_found"])

    @staticmethod
    def wait_timecodes(message, bot, db, user):
        chat_id = int(user.chat_id)
        language = user.language

        timecodes = YoutubeDownloader.parse_description(message.text)

        if timecodes:
            video_length = SubCommand.get_video_length(user.url)

            if SubCommand.has_time_exceeding(timecodes, video_length) is not True:
                session = db.Session()
                db.set_songs(session, user.id, timecodes)
                session.close()

                report = (report_text[language]["info_segments"] +
                          SubCommand.format_tracklist_to_text(timecodes))

                handle_markup(bot, chat_id, report, ["Download All", "Start over"])

            else:
                bot.send_message(chat_id, report_text[language]["exceeds_video"])
        else:
            bot.send_message(chat_id, report_text[language]["not_found"])


class SubCommand:
    """
    A class for encapsulating subcommands and their associated functions.
    """

    @staticmethod
    def format_tracklist_to_text(data):

        if data is None:
            return

        text = ""
        for i, item in enumerate(data, 1):
            timestamp, description = item
            text += f"{i}) {timestamp} - {description}\n"
        return text

    @staticmethod
    def find_songs_in_description(url):
        downloader = YoutubeDownloader(url)
        tracklist = downloader.get_timetamps()
        return tracklist

    @staticmethod
    def get_video_length(url):
        downloader = YoutubeDownloader(url)
        video_time = downloader.get_video_length()
        format_time = f"{video_time.tm_hour:02d}:{video_time.tm_min:02d}:{video_time.tm_sec:02d}"
        return format_time

    @staticmethod
    def save_tracklist(db, user, tracklist):
        try:
            session = db.Session()
            db.create_parameters(session, user.id)
            db.set_songs(session, user.id, tracklist)
            session.close()
        except Exception:
            return False
        return True

    @staticmethod
    def save_url(db, user, url):
        try:
            session = db.Session()
            user = db.get_user(session, user.id)
            user.url = url
            session.commit()
            session.close()
        except:
            return False
        return True

    @staticmethod
    def get_songs_by_user(user, db):
        session = db.Session()
        songs_with_timecodes = db.get_songs(session, user.id)
        session.close()
        return songs_with_timecodes

    @staticmethod
    def get_selected_songs_by_user(user, db):
        session = db.Session()
        selected_songs = db.get_selected_songs(session, user.id)
        session.close()
        selected_songs = list(map(int, selected_songs))
        return selected_songs

    @staticmethod
    def multiple_download(user, db, bot, only_selected_songs=None):
        chat_id = user.chat_id
        language = user.language

        songs_with_timecodes = SubCommand.get_songs_by_user(user, db)

        downloader = YoutubeDownloader(url=user.url,
                                       output_folder=f'{chat_id}_videos')

        local_video_filename = downloader.download()

        if os.path.exists(local_video_filename):
            converter = VideoConverter(local_video_filename, f'{chat_id}_audios')
            list_local_filename = converter.split_video_and_convert_to_audio(timecodes=songs_with_timecodes,
                                                                             selected_songs=only_selected_songs)

            for audiofile in list_local_filename:
                print(audiofile)
                with open(f"{chat_id}_audios/{audiofile}", 'rb') as audio:
                    bot.send_audio(chat_id, audio)

            downloader.clean_output_folder()
            converter.clean_output_folder()

            return

        bot.send_message(chat_id, report_text[language]["error"])

    @staticmethod
    def has_time_exceeding(time_list, target_time):
        def time_to_seconds(time_str):
            parts = list(map(int, time_str.split(':')))
            return sum(x * 60 ** i for i, x in enumerate(reversed(parts[-3:])))

        target_seconds = time_to_seconds(target_time)
        return any(time_to_seconds(time[0]) > target_seconds for time in time_list)
