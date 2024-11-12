from abc import ABC
from fastapi import Request
#
from constants.payload_type import RequestPayloadType
#
from start_utils import logger


class IController(ABC):

    def __init__(self, urn: str = None) -> None:
        super().__init__()
        self.urn = urn
        self.logger = logger.bind(urn=self.urn)

    async def validate_request(self, request: Request) -> None:

        if self.payload_type == RequestPayloadType.JSON:
            self.request_payload = dict(await request.json())

        if self.payload_type == RequestPayloadType.FORM:
            self.request_payload = dict(await request.form())
        