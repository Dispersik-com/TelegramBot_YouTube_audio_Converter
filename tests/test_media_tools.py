import os
import tempfile
import unittest
from unittest.mock import MagicMock
from utils.media_tools import YoutubeDownloader, VideoConverter

class TestYoutubeDownloader(unittest.TestCase):
    def setUp(self):
        self.test_video_url = 'https://www.youtube.com/watch?v=test_video'
        self.output_folder = tempfile.mkdtemp()
        self.youtube_downloader = YoutubeDownloader(self.test_video_url, self.output_folder)
        self.mocked_yt = MagicMock()
        self.mocked_yt.streams.get_audio_only = MagicMock(return_value=self.mocked_yt)
        self.mocked_yt.title = 'Test Video Title'
        self.youtube_downloader.youtube_obj = self.mocked_yt

    def tearDown(self):
        self.youtube_downloader = None
        os.rmdir(self.output_folder)

    def test_download(self):
        downloaded_video = self.youtube_downloader.download()
        expected_filename = f"{self.output_folder}/Test_Video_Title.mp4"
        self.assertTrue(os.path.exists(downloaded_video))
        self.assertEqual(downloaded_video, expected_filename)

    def test_get_description(self):
        self.mocked_yt.description = 'This is a test description.'
        description = self.youtube_downloader.get_description()
        self.assertEqual(description, self.mocked_yt.description)

    def test_get_video_length(self):
        self.mocked_yt.length = 3600  # 1 hour
        time_struct = self.youtube_downloader.get_video_length()
        self.assertEqual(time_struct.tm_hour, 1)

    def test_parse_description(self):
        test_cases = [
            ("01:02 Song Title", [['01:02', 'Song Title']]),
            ("02:45:30 Long Song Title", [['02:45:30', 'Long Song Title']]),
            ("01:02 Song 1\n03:15 Song 2\n00:59 Song 3",
             [['00:59', 'Song 3'], ['01:02', 'Song 1'], ['03:15', 'Song 2']]),
            ("No Timecode", []),
            ("04:30", []),
            ("05:45\\nAnother Song", []),
            ("06:15 Yet Another Song", [['06:15', 'Yet Another Song']]),
            ("01:02 Song 1\n00:59 Song 3\n03:15 Song 2",
             [['00:59', 'Song 3'], ['01:02', 'Song 1'], ['03:15', 'Song 2']]),
        ]

        for description, expected_result in test_cases:
            self.assertEqual(YoutubeDownloader.parse_description(description), expected_result)

    def test_get_timestamps(self):
        test_description = "00:00:00 First Song\n00:03:45 Second Song"
        self.mocked_yt.description = test_description
        timestamps = self.youtube_downloader.get_timetamps()
        expected_result = [['00:00:00', 'First Song'], ['00:03:45', 'Second Song']]
        self.assertEqual(timestamps, expected_result)


class TestVideoConverter(unittest.TestCase):
    def setUp(self):
        self.test_video_file = 'test_video.mp4'
        self.test_video_duration = 60  # seconds
        self.output_folder = tempfile.mkdtemp()
        self.video_converter = VideoConverter(self.test_video_file, self.output_folder)

    def tearDown(self):
        self.video_converter = None
        os.rmdir(self.output_folder)

    def test_create_converter_with_video(self):
        self.assertIsNotNone(self.video_converter._create_converter())

    def test_create_converter_with_audio_only(self):
        # Test with an audio-only file
        audio_only_file = 'test_audio.mp3'
        video_converter = VideoConverter(audio_only_file, self.output_folder)
        self.assertIsNotNone(video_converter._create_converter())

    def test_create_converter_error(self):
        # Test with a non-existing file
        non_existing_file = 'non_existing.mp4'
        video_converter = VideoConverter(non_existing_file, self.output_folder)
        with self.assertRaises(Exception):
            video_converter._create_converter()

    def test_convert_to_audio(self):
        output_format = 'mp3'
        audio_file = self.video_converter.convert_to_audio(output_format)
        self.assertTrue(os.path.exists(audio_file))

    def test_split_video_and_convert_to_audio(self):
        timecodes = [['00:00', 'Song1'], ['00:30', 'Song2']]
        audio_files = self.video_converter.split_video_and_convert_to_audio(timecodes)
        self.assertTrue(all(os.path.exists(os.path.join(self.output_folder, f'{song[1]}.mp3')) for song in timecodes))
        self.assertEqual(len(audio_files), len(timecodes))

    def test_split_video_and_convert_to_audio_with_selected_songs(self):
        timecodes = [['00:00', 'Song1'], ['00:30', 'Song2'], ['01:00', 'Song3']]
        selected_songs = [1, 3]
        audio_files = self.video_converter.split_video_and_convert_to_audio(timecodes, selected_songs=selected_songs)
        self.assertTrue(all(os.path.exists(os.path.join(self.output_folder, f'{song[1]}.mp3')) for song in timecodes))
        self.assertTrue(os.path.exists(os.path.join(self.output_folder, 'Song1.mp3')))
        self.assertFalse(os.path.exists(os.path.join(self.output_folder, 'Song2.mp3')))
        self.assertTrue(os.path.exists(os.path.join(self.output_folder, 'Song3.mp3')))
        self.assertEqual(len(audio_files), len(selected_songs))

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()