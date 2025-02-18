from collections import defaultdict
import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    DOWNLOAD_DIR,
    EXPECTED_STATUS,
    MAIN_DOC_URL,
    PEP_LIST_URL,
    PEP_URL,
)
from exceptions import ParserException, ParserFindUrlException
from outputs import control_output
from utils import find_tag, get_soup

CONNECTION_MESSAGE_ERROR = 'Не удается подключиться к {url}, ошибка: {error}'
DOWNLOAD_MESSAGE_INFO = 'Архив был загружен и сохранён: {archive_path}'
END_LOG_INFO = 'Парсер завершил работу.'
PARSER_LOG_ERROR = 'Работа парсера вызвала ошибку: {error}'
PEP_LOG_INFO = (
    '{tr_link}\n'
    'Статус в карточке: {pep_status}\n'
    'Ожидаемые статусы:'
    '{tr_status}'
)
MAIN_LOG_INFO = 'Аргументы командной строки {args}'
MESSAGE_ERROR = 'Ничего не нашлось'
START_LOG_INFO = 'Парсер запущен!'


def get_main_status(tr_tag):
    try:
        return EXPECTED_STATUS[find_tag(tr_tag, 'abbr').text[1]]
    except (TypeError, IndexError):
        return 'Some unknown status'


def get_single_status(soup):
    for dt_tag in soup.find_all('dt'):
        if dt_tag.text == 'Status:':
            pep_status = dt_tag.find_next_sibling().string
    return pep_status


def whats_new(session):
    """
    Метод возвращает все вышедшие новвоведения в Python.
    Ссылки, заголовки и авторов данных нововведений.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    a_tags = get_soup(session, whats_new_url).select(
        '#what-s-new-in-python div.toctree-wrapper '
        'li.toctree-l1 a[href$=".html"]',
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for a_tag in tqdm(a_tags):
        version_link = urljoin(whats_new_url, a_tag['href'])
        try:
            soup = get_soup(session, version_link)
        except ConnectionError as error:
            logging.error(
                CONNECTION_MESSAGE_ERROR.format(url=version_link, error=error)
            )
            continue
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        results.append((version_link, h1.text, dl.text.replace('\n', ' ')))

    return results


def latest_versions(session):
    """
    Метод возвращает ссылки на документации
    каждой отдельной версии Python, также их статус.
    """
    sidebar = find_tag(
        get_soup(session, MAIN_DOC_URL),
        'div',
        attrs={'class': 'sphinxsidebarwrapper'},
    )

    for ul in sidebar.find_all('ul'):
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindUrlException(MESSAGE_ERROR)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))

    return results


def download(session):
    """Метод скачивает и сохраняет новейшую документацию Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    archive_url = urljoin(
        downloads_url,
        get_soup(session, downloads_url).select_one(
            'table.docutils a[href$="pdf-a4.zip"]'
        )['href'],
    )
    download_dir = BASE_DIR / DOWNLOAD_DIR
    download_dir.mkdir(exist_ok=True)

    response = session.get(archive_url)
    archive_path = download_dir / archive_url.split('/')[-1]
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(DOWNLOAD_MESSAGE_INFO.format(archive_path=archive_path))


def pep(session):
    """Метод возвращает все документы PEP, их типы и статусы."""
    table = find_tag(get_soup(session, PEP_LIST_URL), 'tbody')
    counts_statuses = defaultdict(int)
    not_equals_statuses = []
    tr_tags = table.find_all('tr')
    for tr_tag in tqdm(tr_tags):
        tr_status = get_main_status(tr_tag)
        tr_link = urljoin(PEP_URL, find_tag(tr_tag, 'a')['href'])
        try:
            soup = get_soup(session, tr_link)
        except ConnectionError as error:
            raise CONNECTION_MESSAGE_ERROR.format(
                url=tr_link,
                error=error,
            )
        pep_status = get_single_status(soup)
        if pep_status not in tr_status:
            not_equals_statuses.append(
                PEP_LOG_INFO.format(
                    tr_link=tr_link,
                    pep_status=pep_status,
                    tr_status=tr_status,
                )
            )
        counts_statuses[pep_status] += 1

    list(map(logging.info, not_equals_statuses))
    return [
        ('Статус', 'Количество'),
        *counts_statuses.items(),
        ('Всего', sum(counts_statuses.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info(START_LOG_INFO)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(MAIN_LOG_INFO.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)

        if results is not None:
            control_output(results, args)
    except ParserException as error:
        logging.exception(PARSER_LOG_ERROR.format(error=error))
    logging.info(END_LOG_INFO)


if __name__ == '__main__':
    main()
