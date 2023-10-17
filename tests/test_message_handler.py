import unittest
from unittest.mock import Mock
from utils.handlers.message_handler import StateMachine


class TestStateMachine(unittest.TestCase):
    def setUp(self):
        # Создаем экземпляр StateMachine с примером графа состояний
        self.state_machine = StateMachine({
            'state1': {'options': ['state2', 'state3'], 'command': 'cmd1', 'text': 'Text 1'},
            'state2': {'options': ['state1', 'state3'], 'command': 'cmd2', 'text': 'Text 2'},
            'state3': {'options': ['state1', 'state2'], 'command': 'cmd3', 'text': 'Text 3'},
        })

    def test_has_next(self):
        self.assertTrue(self.state_machine.has_next('state1', 'state2'))
        self.assertFalse(self.state_machine.has_next('state1', 'state1'))

    def test_state_exists(self):
        self.assertTrue(self.state_machine.state_exists('state1'))
        self.assertFalse(self.state_machine.state_exists('state4'))

    def test_get_state(self):
        state = self.state_machine.get_state('state1')
        self.assertEqual(state['state_name'], 'state1')
        self.assertEqual(state['text'], 'Text 1')
        self.assertEqual(state['command'], 'cmd1')


if __name__ == '__main__':
    unittest.main()