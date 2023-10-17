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

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return super(MiddlewareLogger, self).__getattr__(name)
        elif name in self.excluded_methods:
            return getattr(self.target_class, name)
        else:
            return self.wrap_method(getattr(self.target_class, name), name)

    def wrap_method(self, method, name):
        def wrapped(*args, **kwargs):
            try:
                logging.info(f"{self.log_prefix}: '{name}' with args: {args}, kwargs: {kwargs}")
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

