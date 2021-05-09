import json

from enum import Enum
from datetime import datetime

from managers.requests_models import RequestInfo
from managers.requests_models import Request
from managers.requests_models import AuthRequest
from managers.requests_models import MessageRequest
from managers.response_models import AuthResponse


class AuthStatus(Enum):
    FAILURE = 0
    SUCCESS = 1


class TypesRequests:
    AUTH = "AuthRequest"
    MESSAGE = "MessageRequest"


class RequestManager:
    def __init__(self, data: str):
        self.data = data
        self.request = self.parse_request()
        self.type_request_ = self.parse_type_request()
        self.data_request_ = self.parse_data_request()

    def parse_request(self):
        return Request(**json.loads(self.data.decode('utf-8')))

    def parse_type_request(self) -> str:
        return self.request.request[0].type_request

    def parse_data_request(self):
        if self.type_request_ == TypesRequests.AUTH:
            return AuthRequest(**self.request.data[0])
        elif self.type_request_ == TypesRequests.MESSAGE:
            return MessageRequest(**self.request.data[0])

    def type_request(self) -> str:
        return self.type_request_

    def data_request(self):
        return self.data_request_

    def create_response(self, response):
        return response.json()

    def auth_response(self, status_code: int):
        """This function return a response about success or non sucess authorization.
        :param status_code: AuthStatus.SUCCESS or AuthStatus.FAILURE
        """
        r_type = RequestInfo(type_request="AuthResponse", request_ts=f"{datetime.now()}")
        if status_code == AuthStatus.SUCCESS:
            r_data = AuthResponse(access=True)
        elif status_code == AuthStatus.FAILURE:
            r_data = AuthResponse(access=False)
        return Request(request=[r_type], data=[r_data])