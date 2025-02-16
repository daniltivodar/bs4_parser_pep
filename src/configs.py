import logging
from logging.handlers import RotatingFileHandler

import argparse

from constants import BASE_DIR, DATETIME_FORMAT, LOG_FORMAT


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
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных',
    )
    return parser


def configure_logging():
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        datefmt=DATETIME_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(
            RotatingFileHandler(
                log_dir / 'parser.log',
                maxBytes=10**6,
                backupCount=5,
            ),
            logging.StreamHandler(),
        ),
    )
