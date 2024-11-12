from typing import Final


class RequestPayloadType:

    JSON: Final[str] = 'json'
    FORM: Final[str] = 'form'
    FILES: Final[str] = 'files'
    QUERY: Final[str] = 'query'

class ResponsePlayloadType:

    JSON: Final[str] = 'json'
    TEXT: Final[str] = 'text'
    CONTENT: Final[str] = 'content'