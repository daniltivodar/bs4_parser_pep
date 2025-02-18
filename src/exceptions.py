class ParserException(Exception):
    """Вызывается, когда в парсере возникает ошибка."""


class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""


class ParserFindUrlException(Exception):
    """Вызывается, когда парсер не может найти ссылку."""
