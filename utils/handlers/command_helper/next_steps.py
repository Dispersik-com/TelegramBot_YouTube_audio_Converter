from utils.media_tools import is_youtube_url
from utils.handlers.handle_markup import handle_markup
from utils.handlers.command_helper.sub_command import *
from bot_communication_logic.report_messages import Languages
import re


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

                func(url, bot, db, user)

                if save_url(db, user, url) is not True:
                    bot.send_message(chat_id, report_text[language]["error"])
            else:
                handle_markup(bot, user.chat_id,
                              report_text[language]["invalid_link"],
                              report_text[language]['invalid_link_buttons'])
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
        tracklist = find_songs_in_description(url)
        if tracklist is None:
            handle_markup(bot, user.chat_id, report_text[language]["not_found_description"],
                          report_text[language]["invalid_link_buttons"])

        if save_tracklist(db, user, tracklist):
            tracklist_text = (f"{report_text[language]['found_songs']}: "
                              f"\n\n{format_tracklist_to_text(tracklist)}")
            bot.send_message(user.chat_id, tracklist_text)
        else:
            handle_markup(bot, user.chat_id,  report_text[language]["error"],
                          report_text[language]["invalid_link_buttons"])

    @staticmethod
    def wait_select_language(message, bot, db, user):
        chat_id = int(user.chat_id)
        language = "EN"
        if message.text in Languages:
            session = db.Session()
            if db.update_user_language(session, user.id, message.text):
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
            db.create_selected_songs(session, user.id, selected_song_indices)
            songs = db.get_songs(session, user.id)
            session.close()

            selected_songs = list(filter(lambda x: songs.index(x) + 1 in selected_song_indices, songs))

            report = (report_text[language]["info_selected"] +
                      format_tracklist_to_text(selected_songs))

            handle_markup(bot, chat_id, report, report_text[language]["select_songs_buttons"])
        else:
            bot.send_message(chat_id, report_text[language]["not_found"])

    @staticmethod
    def wait_timecodes(message, bot, db, user):
        chat_id = int(user.chat_id)
        language = user.language

        timecodes = YoutubeDownloader.parse_description(message.text)

        if timecodes:
            video_length = get_video_length(user.url)

            if has_time_exceeding(timecodes, video_length) is not True:
                session = db.Session()
                db.update_songs(session, user.id, timecodes)
                session.close()

                report = (report_text[language]["info_segments"] +
                          format_tracklist_to_text(timecodes))

                handle_markup(bot, chat_id, report, report_text[language]["select_songs_buttons"])

            else:
                bot.send_message(chat_id, report_text[language]["exceeds_video"])
        else:
            bot.send_message(chat_id, report_text[language]["not_found"])
