import logging
import sys


FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"


def get_file_handler(
    filename: str, level=logging.INFO, fmt=FORMAT
) -> logging.FileHandler:
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(fmt))

    return file_handler


def get_stream_handler(
    stream=sys.stdout, level=logging.INFO, fmt=FORMAT
) -> logging.StreamHandler:
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter(fmt))

    return stream_handler


def get_logger(name: str, level=logging.DEBUG, handlers: list = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not handlers:
        handlers = [get_stream_handler()]

    for handler in handlers:
        logger.addHandler(handler)

    return logger
