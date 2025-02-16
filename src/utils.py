import logging
from requests import RequestException

from constants import EXPECTED_STATUS
from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True,
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_main_status(tr_tag):
    try:
        tr_status = EXPECTED_STATUS[find_tag(tr_tag, 'abbr').text[1]]
    except (TypeError, IndexError):
        tr_status = 'Some unknown status'
    return tr_status


def get_single_status(soup):
    for dt_tag in soup.find_all('dt'):
        if dt_tag.text == 'Status:':
            pep_status = dt_tag.find_next_sibling().string
    return pep_status
