import json
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.handlers.database_handler import DatabaseHandler, Base, User


class TestDatabaseHandler(unittest.TestCase):
    def setUp(self):
        self.db_url = 'sqlite:///test_db.db'
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        # Удаляем временную базу данных после тестов
        Base.metadata.drop_all(self.engine)

    def test_add_user(self):
        # Тест добавления пользователя
        db = DatabaseHandler(self.db_url)
        session = db.Session()
        user = db.add_user(session, chat_id=1, first_name='John', last_name='Doe', state='active')
        self.assertIsNotNone(user)

    def test_get_user(self):
        # Тест получения пользователя
        db = DatabaseHandler(self.db_url)
        session = db.Session()
        db.add_user(session, chat_id=1, first_name='John', last_name='Doe', state='active')
        user = db.get_user(session, user_id=1)
        self.assertIsNotNone(user)

    def test_update_state(self):
        # Тест обновления состояния пользователя
        db = DatabaseHandler(self.db_url)
        session = db.Session()
        db.add_user(session, chat_id=1, first_name='John', last_name='Doe', state='active')
        db.update_state(session, user_id=1, new_state='inactive')
        user = db.get_user(session, user_id=1)
        self.assertEqual(user.state, 'inactive')

    def test_create_parameters(self):
        db = DatabaseHandler(self.db_url)
        session = db.Session()
        user = db.add_user(session, chat_id=1, first_name='John', last_name='Doe', state='active')
        db.create_parameters(session, user.id)
        parameters = db.get_parameters(session, user.id)

        self.assertIsNotNone(parameters)
        self.assertEqual(parameters.user_id, user.id)
        self.assertIsNone(parameters.sangs_format)

        # Тестируем создание параметров с заданием формата песен
        songs_format = 'mp3'
        parameters_with_format = db.create_parameters(session, user.id, songs_format=songs_format)
        self.assertIsNotNone(parameters_with_format)
        self.assertEqual(parameters_with_format.user_id, user.id)
        self.assertEqual(parameters_with_format.songs_format, songs_format)
        #
        # Проверяем, что повторное создание параметров для того же пользователя не изменяет формат
        parameters_updated = db.create_parameters(session, user.id, songs_format='wav')
        self.assertNotEqual(parameters_updated.songs_format, songs_format)

    def test_get_parameters(self):
        # Тест получения параметров пользователя
        db = DatabaseHandler(self.db_url)
        session = db.Session()
        user = db.add_user(session, chat_id=1, first_name='John', last_name='Doe', state='active')
        db.create_parameters(session, user.id)
        parameters = db.get_parameters(session, user.id)
        print(parameters)
        self.assertIsNotNone(parameters)

    def test_selected_songs(self):
        # Тест сохранения и получения выбранных песен
        db = DatabaseHandler(self.db_url)
        session = db.Session()
        user = db.add_user(session, chat_id=1, first_name='John', last_name='Doe', state='active')
        db.create_parameters(session, user.id)

        # Тестируем сохранение
        selected_songs = [1, 2, 3]
        result = db.set_selected_songs(session, user.id, selected_songs)
        parameters = db.get_parameters(session, user.id)
        self.assertTrue(result)
        self.assertEqual(json.loads(parameters.selected_songs), selected_songs)

        # Тестируем получение
        retrieved_songs = db.get_selected_songs(session, user.id)
        self.assertEqual(retrieved_songs, selected_songs)

    def test_add_and_get_songs(self):
        # Тест добавления и получения песен
        db = DatabaseHandler(self.db_url)
        session = db.Session()
        user = db.add_user(session, chat_id=1, first_name='John', last_name='Doe', state='active')
        db.create_parameters(session, user.id)

        # Тестируем добавление песен
        songs_to_add = [['01:30', 'Song 1'], ['02:45', 'Song 2']]
        result = db.set_songs(session, user.id, songs_to_add)
        self.assertTrue(result)

        # Тестируем получение песен
        retrieved_songs = db.get_songs(session, user.id)
        self.assertEqual(retrieved_songs, songs_to_add)

        # Дополнительно можно проверить, что получение песен для другого пользователя возвращает None
        other_user = db.add_user(session, chat_id=2, first_name='Alice', last_name='Smith', state='active')
        songs_for_other_user = db.get_songs(session, other_user.id)
        self.assertIsNone(songs_for_other_user)


if __name__ == '__main__':
    unittest.main()