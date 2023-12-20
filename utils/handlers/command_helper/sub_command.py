import os
from utils.media_tools import YoutubeDownloader, VideoConverter
from bot_communication_logic.report_messages import report_text


def format_tracklist_to_text(data):

    if data is None:
        return

    text = ""
    for i, item in enumerate(data, 1):
        timestamp, description = item
        text += f"{i}) {timestamp} - {description}\n"
    return text


def find_songs_in_description(url):
    downloader = YoutubeDownloader(url)
    tracklist = downloader.get_timestamps()
    return tracklist


def get_video_length(url):
    downloader = YoutubeDownloader(url)
    video_time = downloader.get_video_length()
    format_time = f"{video_time.tm_hour:02d}:{video_time.tm_min:02d}:{video_time.tm_sec:02d}"
    return format_time


def save_tracklist(db, user, tracklist):
    try:
        session = db.Session()
        db.create_parameters(session, user.id)
        db.set_songs(session, user.id, tracklist)
        session.close()
    except Exception:
        return False
    return True


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


def get_songs_by_user(user, db):
    session = db.Session()
    songs_with_timecodes = db.get_songs(session, user.id)
    session.close()
    return songs_with_timecodes


def get_selected_songs_by_user(user, db):
    session = db.Session()
    selected_songs = db.get_selected_songs(session, user.id)
    session.close()
    selected_songs = list(map(int, selected_songs))
    return selected_songs


def multiple_download(user, db, bot, only_selected_songs=None):
    chat_id = user.chat_id
    language = user.language

    songs_with_timecodes = get_songs_by_user(user, db)

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


def has_time_exceeding(time_list, target_time):
    def time_to_seconds(time_str):
        parts = list(map(int, time_str.split(':')))
        return sum(x * 60 ** i for i, x in enumerate(reversed(parts[-3:])))

    target_seconds = time_to_seconds(target_time)
    return any(time_to_seconds(time[0]) > target_seconds for time in time_list)