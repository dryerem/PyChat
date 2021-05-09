from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class RequestInfo(BaseModel):
    type_request: str
    request_ts: Optional[datetime] = None


class Request(BaseModel):
    request: List[RequestInfo]
    data: list

class AuthRequest(BaseModel):
    login: str
    password: str


class MessageRequest(BaseModel):
    message: str
    from_: str
    to: str


if __name__ == "__main__":
    print(Request(request=[{"type_request":"AuthRequest", "request_ts": f"{datetime.now()}"}], data=[AuthRequest(login="admin", password="admin")]))
    #print(AuthRequest(request=[{"type_request":"auth", "request_ts": f"{datetime.now()}"}], login="admin", password="admin"))
    #print(MessageRequest(request=[{"type_request":"message", "request_ts": f"{datetime.now()}"}], from_="admin", to="all"))