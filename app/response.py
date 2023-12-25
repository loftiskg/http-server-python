from dataclasses import dataclass, field
from typing import Dict

from app.constants import CLRF

@dataclass
class Response:
    protocol: str = "HTTP/1.1"
    status_code: int = 200
    status_text: str = 'OK'
    headers: Dict[str, str] = field(default_factory=dict)
    body: str | None = None


def response_200_ok():
    return Response(status_code=200, status_text='OK')
def response_404_not_found():
    return Response(status_code=404, status_text='Not Found')
def response_201_created():
    return Response(status_code=201, status_text='Created')



def encode_http_response(response: Response):
    protocol, status_code, status_text = response.protocol, response.status_code, response.status_text
    start_line = f"{protocol} {status_code} {status_text}" + CLRF
    response_encoded = [start_line]

    if response.headers:
        response_encoded += [f"{key}: {value}" + CLRF for (key, value) in response.headers.items()]
    if response.body:
        response_encoded.append(CLRF)
        response_encoded.append(response.body+CLRF)     

    r = (''.join(response_encoded) + CLRF).encode()
    return r