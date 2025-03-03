import logging

from colorlog import ColoredFormatter


def get_logger(name: str) -> logging.Logger:
    """Создаёт и настраивает логгер."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = ColoredFormatter(
        '%(log_color)s%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%',
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger
