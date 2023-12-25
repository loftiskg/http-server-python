from dataclasses import dataclass
from typing import Dict


@dataclass
class Request:
    method: str
    path: str
    protocol: str
    headers: Dict[str, str]
    body: str

def parse_http_request(request_data: str) -> Request:
    lines = request_data.splitlines()
    start_line = lines[0]
    method, path, protocol = start_line.split()

    headers = {}
    for line in lines[1:]:
        if line == "":
            break
        key, value = line.split(": ")
        headers[key] = value

    body = "\n".join(lines[lines.index("")+1:])

    return Request(method, path, protocol, headers, body)