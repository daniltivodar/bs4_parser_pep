import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    DATETIME_FORMAT,
    LOG_DIR,
    LOG_FORMAT,
    OUTPUT_FILE,
    OUTPUT_PRETTY,
)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        help='Режимы работы парсера',
        choices=available_modes,
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        help='Очистка кеша',
        action='store_true',
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(OUTPUT_PRETTY, OUTPUT_FILE),
        help='Дополнительные способы вывода данных',
    )
    return parser


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        datefmt=DATETIME_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(
            RotatingFileHandler(
                LOG_DIR / 'parser.log',
                maxBytes=10**6,
                backupCount=5,
            ),
            logging.StreamHandler(),
        ),
    )
