from typing import Dict
import requests

class APIClient:
    def __init__(self, base_url: str , headers: Dict = None, timeout: int =10):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.timeout = timeout

    def get(self, endpoint: str , params:Dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Dict = None, json: Dict = None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, data=data, json=json, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
