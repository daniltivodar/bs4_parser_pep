import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR,
    DATETIME_FORMAT,
    OUTPUT_DEFAULT,
    OUTPUT_FILE,
    OUTPUT_PRETTY,
    RESULTS_DIR,
)

COMPLETE_MESSAGE = 'Файл с результатами был сохранён: {file_path}'


def control_output(results, cli_args):
    OUTPUT_CHOICES[cli_args.output](results, cli_args)


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    file_path = results_dir / (
        f'{cli_args.mode}_{dt.datetime.now().strftime(DATETIME_FORMAT)}.csv'
    )
    with open(file_path, 'w', encoding='utf-8') as file:
        csv.writer(file, csv.unix_dialect).writerows(results)
    logging.info(COMPLETE_MESSAGE.format(file_path=file_path))


OUTPUT_CHOICES = {
    OUTPUT_PRETTY: pretty_output,
    OUTPUT_FILE: file_output,
    OUTPUT_DEFAULT: default_output,
}
