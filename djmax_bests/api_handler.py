import requests
from . import models


def build_req_url(username: str, bmode: str, board: str) -> str:
    base_url = f"https://v-archive.net/api/archive/{username}/board/{bmode}/{board}"
    return base_url

def fetch_board_data(username: str, bmode: str, board: str) -> models.DMBests:
    url = build_req_url(username, bmode, board)
    response = requests.get(url)
    response.raise_for_status()
    va_resp = models.VAResponse.model_validate_json(response.text)
    return models.DMBests.from_VAResponse(username, bmode, va_resp)
