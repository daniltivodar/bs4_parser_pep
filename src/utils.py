from requests import RequestException

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException

CONNECTION_MESSAGE_ERROR = 'Не удается подключиться к {url}, ошибка: {error}'
FIND_TAG_MESSAGE_ERROR = 'Не найден тег {tag} {attrs}'


def get_response(session, url, encoding='utf-8'):
    """Метод возвращает ответ с веб-сайта."""
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(
            CONNECTION_MESSAGE_ERROR.format(url=url, error=error),
        )


def get_soup(session, url, features='lxml'):
    """Метод возвращает суп."""
    return BeautifulSoup(get_response(session, url).text, features=features)


def find_tag(soup, tag, attrs=None):
    """Метод находит тег."""
    searched_tag = soup.find(tag, attrs={} if attrs is None else attrs)
    if searched_tag is None:
        raise ParserFindTagException(
            FIND_TAG_MESSAGE_ERROR.format(tag=tag, attrs=attrs),
        )
    return searched_tag
