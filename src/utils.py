from requests import RequestException

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException

CONNECTION_MESSAGE_ERROR = 'Не удается подключиться к {url}'
FIND_TAG_MESSAGE_ERROR = 'Не найден тег {tag} {attrs}'


def get_response(session, url, style='utf-8'):
    """Метод возвращает ответ с веб-сайта."""
    try:
        response = session.get(url)
        response.encoding = style
        return response
    except RequestException:
        raise ConnectionError(CONNECTION_MESSAGE_ERROR.format(url=url))


def get_soup(session, url):
    """Метод возвращает суп."""
    return BeautifulSoup(get_response(session, url).text, features='lxml')


def find_tag(soup, tag, attrs=None):
    """Метод находит тег."""
    searched_tag = soup.find(tag, attrs={} if attrs is None else attrs)
    if searched_tag is None:
        raise ParserFindTagException(
            FIND_TAG_MESSAGE_ERROR.format(tag=tag, attrs=attrs),
        )
    return searched_tag
