EN_state_graph = {
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
        'command': "select_songs",
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

UA_state_graph = {
    '/start': {
        'text': "Привіт, я бот-конвертер. Ви можете надіслати мені посилання на відео чи пісню, "
                "і я конвертуватиму її у звуковий файл та відправлю вам. Крім того, "
                "я можу розділити відео на окремі сегменти за часовими мітками, наданими в описі, "
                "і відправити їх вам.",
        'command': None,
        'options': [
            "Відео із піснею",
            "Відео з часовими мітками",
        ]
    },
    'Відео із піснею': {
        'text': 'Надішліть мені посилання на відео із піснею, і я конвертую його в файл.\n\nОчікую посилання...',
        'command': 'wait_url_from_song',
        'options': [
            'Завантажити',
            'Почати спочатку'
        ]
    },
    'Відео з часовими мітками': {
        'text': 'Надішліть мені посилання на відео з часовими мітками в описі.\n\nОчікую посилання...',
        'command': 'wait_url_video_with_timestamps',
        'options': [
            'Завантажити все',
            'Вибрати',
            'Встановити свої',
            'Почати спочатку'
        ]
    },
    'Завантажити все': {
        'text': 'Процес розпочався...',
        'command': "download_all",
        'options': [
            'Почати спочатку'
        ]
    },
    'Вибрати': {
        'text': 'Напишіть номери пісень у форматі:\n\n "1, 2, 3..."',
        'command': "select_songs",
        'options': [
            'Почати спочатку'
        ]
    },
    'Завантажити вибрані': {
        'text': 'Процес розпочався...',
        'command': "download_selected",
        'options': [
            'Почати спочатку'
        ]
    },
    'Встановити свої': {
        'text': 'Напишіть свої часові мітки у форматі:\n\n "01:02 [назва пісні]\n 03:04 [назва пісні]\n "',
        'command': "set_timecodes",
        'options': [
            'Почати спочатку'
        ]
    },
    'Завантажити': {
        'text': 'Завантаження...',
        'command': 'download',
        'options': [
            'Почати спочатку'
        ]
    },
    'Почати спочатку': {
        'text': 'Виберіть дію',
        'command': 'back',
        'options': [
            "Відео із піснею",
            "Відео з часовими мітками",
        ]
    }
}

state_graph = {
    "EN": EN_state_graph,
    "UA": UA_state_graph
}
