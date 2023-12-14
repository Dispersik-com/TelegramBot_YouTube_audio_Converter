state_graph = {
    '/start': {
        'text': "Hello, I'm a converter bot. You can send me a link to a video or a song,"
                " and I will convert it into an audio file and send it to you. Additionally,"
                " I can split a video into separate segments based on timestamps provided in the description"
                " and send them to you.",
        'command': None,
        'options': [
            "Video with song",
            "Video with timestamps",
        ]
    },
    'Video with song': {
        'text': 'Send me a link to a video with a song, and I will convert it to a file.\n\nWaiting for a link...',
        'command': 'wait_url_from_song',
        'options': [
            'Download',
            'Start over'
        ]
    },
    'Video with timestamps': {
        'text': 'Send me a link to a video with song timestamps in the description.\n\nWaiting for a link...',
        'command': 'wait_url_video_with_timestamps',
        'options': [
            'Download All',
            'Select',
            'Set Your Own',
            'Start over'
        ]
    },
    'Download All': {
        'text': 'The process has started...',
        'command': "download_all",
        'options': [
            'Start over'
        ]
    },
    'Select': {
        'text': 'Write song numbers in the format:\n\n "1, 2, 3..."',
        'command': "choice_songs",
        'options': [
            'Start over'
        ]
    },
    'Download Selected': {
        'text': 'The process has started...',
        'command': "download_selected",
        'options': [
            'Start over'
        ]
    },
    'Set Your Own': {
        'text': 'Write your timestamps in the format:\n\n "01:02 [song name]\n 03:04 [song name]\n "',
        'command': "set_timecodes",
        'options': [
            'Start over'
        ]
    },
    'Download': {
        'text': 'Downloading...',
        'command': 'download',
        'options': [
            'Start over'
        ]
    },
    'Start over': {
        'text': 'Choose an action',
        'command': 'back',
        'options': [
            "Video with song",
            "Video with timestamps",
        ]
    }
}

