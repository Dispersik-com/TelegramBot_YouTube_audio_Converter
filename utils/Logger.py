import copy
import logging
import time


class Logger:
    def __init__(self, log_filename):
        self.log_filename = log_filename

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] - %(message)s",
            handlers=[
                logging.FileHandler(self.log_filename),
                logging.StreamHandler()
            ]
        )


class MiddlewareLogger:
    def __init__(self, target_class, logger: logging,
                 log_prefix: str = 'Calling function',
                 excluded_methods: list = None,
                 debug=False):

        self.target_class = target_class
        self.logger = logger
        self.log_prefix = log_prefix
        self.excluded_methods = set(excluded_methods) if excluded_methods is not None else set()
        self.debug = debug
        self.format_arguments = dict()

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return super(MiddlewareLogger, self).__getattr__(name)
        elif name in self.excluded_methods:
            return getattr(self.target_class, name)
        else:
            return self.wrap_method(getattr(self.target_class, name), name)

    def wrap_method(self, method, name):
        def wrapped(*args, **kwargs):
            formatted_args = self.format_args(args)
            formatted_kwargs = self.format_kwargs(kwargs)

            try:
                logging.info(f"{self.log_prefix}: '{name}' with args: {formatted_args}, kwargs: {formatted_kwargs}")

                result = method(*args, **kwargs)

                if self.debug:
                    if result is not None:
                        logging.info(f"'{name}' returned --> {result}")
                    else:
                        logging.info(f"'{name}' returned --> None or no return value")
                return result
            except Exception as e:
                error_message = f"Error in {name}: {str(e)}"
                logging.error(error_message)
                raise e

        return wrapped

    def format_args(self, args):
        formatted_args = [self.perform_format_argument(arg, self.format_arguments.get(arg.__class__.__name__, lambda x: x)) for arg in args]
        return formatted_args

    def format_kwargs(self, kwargs):
        formatted_kwargs = {key: self.perform_format_argument(value, self.format_arguments.get(value.__class__.__name__, lambda x: x)) for key, value in kwargs.items()}
        return formatted_kwargs

    def add_format_argument_func(self, class_name, format_func):
        self.format_arguments[class_name] = format_func
        return self

    def perform_format_argument(self, argument: object, format_func):
        return format_func(argument)
