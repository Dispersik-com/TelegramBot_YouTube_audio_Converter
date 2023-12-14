
class StateMachine:
    """
    Class for navigating state graphs and managing state transitions.
    Used to determine valid state transitions based on a predefined state graph.
    """
    def __init__(self, state_graph):
        """
        Initialize the StateMachine.

        :param state_graph: A graph representation of available states and transitions.
        """
        self.state_graph = state_graph

    def has_next(self, state, next_state):
        """
        Check if there's a valid transition from the current state to the next state.

        :param state: Current state.
        :param next_state: Potential next state.

        :return: True if the transition is allowed, False otherwise.
        """
        return next_state in self.state_graph[state].get('options')

    def state_exists(self, state):
        """
        Check if the given state exists in the state graph.

        :param state: State to check.

        :return: True if the state exists, False otherwise.
        """
        return state in self.state_graph.keys()

    def get_state(self, state_name):
        """
        Get the state details for a given state name.

        :param state_name: Name of the state.

        :return: State information as a dictionary.
        """
        state = self.state_graph.get(state_name)
        if state is None:
            return
        state['state_name'] = state_name
        return state

    def get_options_for_state(self, state_name):
        """
        Get the actions to be performed for a given state name.

        :param state_name: Name of the state.

        :return: List of actions.
        """
        state = self.state_graph.get(state_name, {})
        return state.get('options', [])