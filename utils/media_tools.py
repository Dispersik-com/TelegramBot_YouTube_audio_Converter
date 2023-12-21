import os
import re
import shutil
import time
import requests
from moviepy.editor import VideoFileClip, AudioFileClip
from pytube import YouTube
from pytube.cli import on_progress
import logging
from bs4 import BeautifulSoup

from pytube.exceptions import RegexMatchError, VideoUnavailable


class MediaProcessor:
    """
    A base class for processing media files.

    :param output_folder: The folder where processed media files will be saved. If not provided, a default folder is used.
    """

    def __init__(self, output_folder=None):
        self.output_folder = output_folder
        if output_folder is None:
            self.output_folder = 'output_folder'

    def clean_output_folder(self):
        """
        Cleans the output folder by deleting all files and the folder itself.

        :return: True if the cleanup is successful, False if an error occurs.
        """
        try:
            # Clean all files in the folder and delete the folder
            for filename in os.listdir(self.output_folder):
                file_path = f"{self.output_folder}/{filename}"
                if os.path.isfile(file_path):
                    os.unlink(file_path)

            # Delete the folder
            shutil.rmtree(self.output_folder)

            return True
        except Exception as e:
            logging.error(f'An error occurred with folder cleanup. Folder:{self.output_folder}. Error: {str(e)}')
            return False


class YoutubeDownloader(MediaProcessor):
    """
    A class for downloading media files from YouTube.

    :param url: The URL of the YouTube video to download.
    :param output_folder: The folder where the downloaded media file will be saved. If not provided, a default folder is used.
    """

    def __init__(self, url, output_folder=None):
        super().__init__(output_folder)
        self.url = url
        self.youtube_obj = None

        try:
            self.youtube_obj = YouTube(self.url)
        except RegexMatchError:
            logging.error("Invalid URL format. Please provide a valid YouTube URL.")
            self.url = None
        except VideoUnavailable:
            logging.error("The video is unavailable. Please check if it's private or deleted.")
            self.url = None
        except Exception as e:
            self.url = None
            logging.error(f"An error occurred: {e}")

    def download(self, track_progress=False):
        """
        Downloads a video from YouTube.

        :param track_progress: If True, track download progress. Default is False.
        :return: The name of the downloaded video or False if an error occurs during the download.
        """
        try:
            yt = self.youtube_obj

            stream = yt.streams.get_audio_only()

            video_title = clean_invalid_chars(yt.title)
            output_filename = f"{video_title}.mp4"

            if track_progress:
                yt.register_on_progress_callback(on_progress)

            stream.download(output_path=self.output_folder, filename=output_filename)

            return f'{self.output_folder}/{output_filename}'
        except Exception as e:
            logging.error(f'An error occurred during video download:{e}')
            return False

    def get_description(self):
        # [YouTube_Object].description it's does't working
        soup = BeautifulSoup(requests.get(self.url, cookies={'CONSENT': 'YES+1'}).text, 'html.parser')
        pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
        description = pattern.findall(str(soup))[0].replace('\\n', '\n')
        return description

    def get_video_length(self):
        """
        Gets the length of the video in seconds.

        :return: A time struct representing the length of the video.
        """
        yt = self.youtube_obj
        total_seconds = yt.length
        time_struct = time.gmtime(total_seconds)
        return time_struct

    @staticmethod
    def parse_description(description: str):
        """
        Parses the video description to extract timestamps and song names.

        :param description: The description text from the video.
        :return: A list of lists, where each inner list contains a timecode and a song name.
        """
        pattern = r'(\d{2}:\d{2}:\d{2}|\d{2}:\d{2})(?:\s(.*?)(?=\d{2}:\d{2}|\n|\\n|$))?'

        matches = re.findall(pattern, description)

        result = []

        for idx, match in enumerate(matches, start=1):
            timecode = match[0]
            song_name = clean_invalid_chars(match[1] if match[1] != '' else f"unknown_timestamp_{idx}")
            result.append([timecode, song_name])

        result = sorted(result, key=lambda item: item[0])

        return result

    def get_timestamps(self):
        description = self.get_description()
        if description is None:
            return None
        return self.parse_description(description)


class VideoConverter(MediaProcessor):
    """
    A class for converting video files to audio.

    :param filename: The path to the video file to be converted.
    :param output_folder: The folder where the converted audio file will be saved.
    """

    def __init__(self, filename, output_folder=None):
        super().__init__(output_folder)
        self.filename = filename

    def _create_converter(self):
        """
        Attempt to create an audio converter from the video.

        :return: An audio converter.
        :raises KeyError: If there are no video frames in the video file, it creates an AudioFileClip object instead.
        :raises Exception: If an error occurs during the conversion.
        """
        try:
            # Attempt to extract audio from the video using moviepy
            clip = VideoFileClip(self.filename)
            clip = clip.audio
            return clip
        except KeyError as key:
            # Handle the case where 'video_fps' key is missing
            if str(key) == "'video_fps'":
                clip = AudioFileClip(self.filename)
                return clip
        except Exception as e:
            raise e

    def convert_to_audio(self, output_format):
        """
        Converts a video file to an audio file in the specified format.
        output_format :param output_format: The format of the output audio file (e.g., 'mp3').
        :return: The path to the converted audio file on success, or None on failure.
        """
        clip = self._create_converter()

        try:
            # Prepare output file names and paths
            filename = os.path.basename(self.filename)
            local_output_path = f"{self.output_folder}/{filename.replace('mp4', output_format)}"

            # Create the output folder if it doesn't exist
            os.makedirs(self.output_folder, exist_ok=True)

            # Write the audio to the output file
            clip.write_audiofile(local_output_path)

            return local_output_path

        except Exception as e:
            # Close the clip to free up resources
            clip.close()
            raise e

    def split_video_and_convert_to_audio(self, timecodes: list[str:str], output_format='mp3', selected_songs=None):
        """
        Splits the video into audio segments based on provided timecodes and converts them to the specified audio format.

        :param timecodes: A list of timecodes and song names (list[list[timecode, song name]]).
        :param output_format: The desired audio format (default is 'mp3').
        :param selected_songs: A list of selected song indices to split and convert. Default is all songs.
        :return: A list of filenames in the output folder.
        """
        try:
            os.makedirs(self.output_folder, exist_ok=True)
            clip = self._create_converter()

            if selected_songs is None:
                selected_songs = list(range(1, len(timecodes) + 1))

            for i in range(len(timecodes)):
                timecode, song_name = timecodes[i]
                start_time = self._timecode_to_int(timecode)

                if i + 1 < len(timecodes):
                    end_time = self._timecode_to_int(timecodes[i + 1][0])
                else:
                    end_time = clip.duration

                # Check if the current song should be cut
                if (i + 1) in selected_songs:
                    audio_subclip = clip.subclip(start_time, end_time)

                    output_audiofile = os.path.join(self.output_folder, f"{song_name}.{output_format}")
                    audio_subclip.write_audiofile(output_audiofile)

            file_list = os.listdir(self.output_folder)
            logging.info('Split and converted video to audio: %s', file_list)
            return file_list
        except Exception as e:
            logging.error(f'An error occurred during video splitting and audio conversion: {str(e)}')
            return []

    def _timecode_to_int(self, timecode):
        time_parts = timecode.split(':')
        if len(time_parts) == 2:
            minutes, seconds = map(int, time_parts)
            total_seconds = minutes * 60 + seconds
        elif len(time_parts) == 3:
            hours, minutes, seconds = map(int, time_parts)
            total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds


def clean_invalid_chars(data):
    """
    Cleans the video title from invalid characters.

    :param data: The title of the video.
    :return: The cleaned video title.
    """
    invalid_chars = r'[\/:*?"<>|,]'
    cleaned_data = re.sub(invalid_chars, '', data)
    return cleaned_data


def is_youtube_url(url):
    """Checks if the URL is valid."""
    youtube_url_pattern = re.compile(
        r"^(https?://)?(www\.)?(youtube\.com|music\.youtube\.com|youtu\.be)/.*$"
    )

    return bool(youtube_url_pattern.match(url))