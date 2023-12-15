from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Base, User, Parameters, Songs
import json


# Define the DatabaseHandler class for working with the database
class DatabaseHandler:
    _instance = None

    # Constructor of the class (implements the Singleton pattern)
    def __new__(cls, db_url: str):
        """
        Create a new instance of the DatabaseHandler if it doesn't exist.

        :param db_url: The URL for the database.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseHandler, cls).__new__(cls)
            cls._instance.db_url = db_url
            cls._instance.engine = create_engine(db_url)
            cls._instance.Session = sessionmaker(bind=cls._instance.engine)
            if not inspect(cls._instance.engine).has_table("Users"):
                cls._instance.create_tables()
        return cls._instance

    # Method to create tables in the database
    def create_tables(self):
        """
        Create database tables if they do not already exist.
        """
        Base.metadata.create_all(self.engine)

    @staticmethod
    def add_user(session, chat_id: int, first_name: str, last_name: str, state: str) -> User:
        """
        Add a new user to the database.

        :param session: SQLAlchemy session object.
        :param chat_id: Chat ID of the user.
        :param first_name: First name of the user.
        :param last_name: Last name of the user (can be None).
        :param state: Current state of the user.

        :return: The newly added User object.
        """
        user = User(chat_id=chat_id,
                    first_name=first_name,
                    last_name=last_name,
                    state=state,
                    previous_state=state)
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def get_user(session, user_id: int):
        """
        Retrieve a user from the database by their ID.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user to retrieve.

        :return: The User object if found, or None if not found.
        """
        user = session.query(User).filter_by(id=user_id).first()
        return user if user is not None else None

    @staticmethod
    def get_user_by_chat_id(session, chat_id: int):
        """
        Retrieve a user from the database by their ID.

        :param session: SQLAlchemy session object.
        :param chat_id: ID of the user to retrieve.

        :return: The User object if found, or None if not found.
        """
        user = session.query(User).filter_by(chat_id=chat_id).first()
        return user if user is not None else None

    @staticmethod
    def update_state(session, user_id: int, new_state: str):
        """
        Update the state of a user in the database.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user to update.
        :param new_state: The new state to set for the user.
        """
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.previous_state = user.state
            user.state = new_state
            session.commit()
            return user
        return False

    @staticmethod
    def get_parameters(session, user_id: int):
        """
        Get the parameters associated with a user.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user.

        :return: Parameters object if found, or None.
        """
        if user_id:
            parameters = session.query(Parameters).filter_by(user_id=user_id).first()
            return parameters
        return None

    @staticmethod
    def create_parameters(session, user_id: int, songs_format='mp3'):
        """
        Create or update user parameters, including songs format.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user.
        :param songs_format: Format for songs (default is 'mp3').

        :return: Parameters object if successful, or None on error.
        """
        try:
            parameters = session.query(Parameters).filter_by(user_id=user_id).first()
            if not parameters:
                parameters = Parameters(user_id=user_id)
                session.add(parameters)

            if songs_format is not None:
                parameters.songs_format = songs_format

            session.commit()
            return parameters
        except Exception as e:
            print(f"Error updating/creating parameters: {e}")
            return None

    @staticmethod
    def update_sangs_format(session, user_id: int, new_format: str):
        """
        Update the songs format for a user's parameters.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user.
        :param new_format: New songs format.

        :return: True if successful, False if no parameters found.
        """
        parameters = DatabaseHandler.get_parameters(session, user_id)

        if parameters:
            parameters.sangs_format = new_format
            session.commit()
            return True

        return False

    @staticmethod
    def set_selected_songs(session, user_id: int, selected_songs: list[int]):
        """
        Set the selected songs for a user.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user.
        :param selected_songs: List of selected songs.

        :return: True if successful, False if no parameters found.
        """
        parameters = session.query(Parameters).filter_by(user_id=user_id).first()

        if selected_songs:
            parameters.selected_songs = json.dumps(selected_songs)
            session.commit()
            return True
        return False

    @staticmethod
    def get_selected_songs(session, user_id: int):
        """
        Get the selected songs for a user.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user.

        :return: List of selected songs.
        """
        parameters = session.query(Parameters).filter_by(user_id=user_id).first()

        if parameters.selected_songs:
            return json.loads(parameters.selected_songs)
        return []

    @staticmethod
    def set_songs(session, user_id: int, songs: list[list[str, str]]) -> bool:
        """
        Set the list of songs for a user.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user.
        :param songs: List of songs to set.

        :return: True if successful, False if no parameters found.
        """
        parameters = DatabaseHandler.get_parameters(session, user_id)

        if parameters:
            session.query(Songs).filter(Songs.Parameters_id == parameters.id).delete()

            for position, (timecode, name) in enumerate(songs, start=1):
                song = Songs(
                    Parameters_id=parameters.id,
                    tracklist_position=position,
                    timecode=timecode,
                    name=name
                )

                session.add(song)

            session.commit()
            return True

        return False

    @staticmethod
    def get_songs(session, user_id: int):
        """
        Get the list of songs for a user.

        :param session: SQLAlchemy session object.
        :param user_id: ID of the user.

        :return: List of songs: list[list[str, str]], or None if no parameters found.
        """
        parameters = DatabaseHandler.get_parameters(session, user_id)

        if parameters:
            songs = session.query(Songs).filter_by(Parameters_id=parameters.id).all()
            song_list = [[song.timecode, song.name] for song in songs]
            return song_list

        return None

    def close(self):
        """
        Close the SQLAlchemy sessions and dispose of the database engine.

        :return: None.
        """
        self.Session.close_all()
        # close_all_sessions() (deprecated since: 1.3)
        self.engine.dispose()
