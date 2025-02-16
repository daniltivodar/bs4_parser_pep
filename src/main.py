import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    MAIN_DOC_URL,
    PEP_LIST_URL,
    PEP_URL,
)
from outputs import control_output
from utils import find_tag, get_main_status, get_response, get_single_status


def whats_new(session):
    """
    Метод возвращает все вышедшие новвоведения в Python.
    Ссылки, заголовки и авторов данных нововведений.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(
        main_div,
        'div',
        attrs={'class': 'toctree-wrapper'},
    )
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'},
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):

        version_link = urljoin(whats_new_url, find_tag(section, 'a')['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        results.append((version_link, h1.text, dl.text.replace('\n', ' ')))

    return results


def latest_versions(session):
    """
    Метод возвращает ссылки на документации
    каждой отдельной версии Python, также их статус.
    """
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(session):
    """Метод скачивает и сохраняет новейшую документацию Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    table = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table,
        'a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')},
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)

    response = session.get(archive_url)
    archive_path = downloads_dir / archive_url.split('/')[-1]
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Метод возвращает все документы PEP, их типы и статусы."""
    response = get_response(session, PEP_LIST_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    table = find_tag(soup, 'tbody')
    results = [('Статус', 'Количество')]
    counts_statuses = {}
    not_equals_statuses = []
    tr_tags = table.find_all('tr')
    for tr_tag in tqdm(tr_tags):
        tr_status = get_main_status(tr_tag)
        tr_link = urljoin(PEP_URL, find_tag(tr_tag, 'a')['href'])
        response = get_response(session, tr_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        pep_status = get_single_status(soup)
        if pep_status not in tr_status:
            not_equals_statuses.append([tr_link, pep_status, tr_status])
        if pep_status in counts_statuses:
            counts_statuses[pep_status] += 1
        else:
            counts_statuses[pep_status] = 1

    total = 0
    for pep_status, count in counts_statuses.items():
        total += count
        results.append((pep_status, count))
    results.append(('total', total))
    for log_info in not_equals_statuses:
        logging.info(
            f'{log_info[0]}\n'
            f'Статус в карточке: {log_info[1]}\n'
            'Ожидаемые статусы:'
            f'{log_info[2]}'
        )
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    results = MODE_TO_FUNCTION[args.mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
