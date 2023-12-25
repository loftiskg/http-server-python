from pathlib import Path
import re
from app.request import Request
from app.response import Response, response_200_ok, response_201_created, response_404_not_found

def root_handler(path: Request) -> Response:
    return response_200_ok()

def echo_handler(request: Request):
    body = re.match(r"/echo/(.*)", request.path).group(1)

    response = response.response_200_ok()
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Length'] = '{}'.format(len(body))
    response.body = body

    return response

def not_found_handler(path: Request) -> Response:
    return response_404_not_found()

def user_agent_handler(request: Request) -> Response:
    user_agent = request.headers["User-Agent"]

    response = response_200_ok()
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Length'] = '{}'.format(len(user_agent))
    response.body = user_agent

    return response

def get_files_handler(request: Request, directory: Path|None) -> Response:
    filename = re.match(r"/files/(.*)", request.path).group(1)
    if directory is None:
        return response_404_not_found()
    else:
        fpath = directory/filename
        if fpath.is_file():
            resp = response_200_ok()
            with fpath.open() as f:
                resp.body = f.read()
            resp.headers['Content-Type'] = 'application/octet-stream'
            resp.headers['Content-Length'] = '{}'.format(len(resp.body))
            return resp
        else:
            print(f"Requested file not found: {fpath}")
            return response_404_not_found()
  
def post_files_handler(request: Request, directory: Path | None) -> Response:
    if directory is None or not directory.is_dir():
        return response_404_not_found()
    else:
        filename = re.match(r"/files/(.*)", request.path).group(1)
        fpath = directory/filename
        with open(fpath, mode='w+') as f:
            f.write(request.body)
        return response_201_created()