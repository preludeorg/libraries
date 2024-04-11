import os 
import requests

from requests.adapters import HTTPAdapter, Retry


PRELUDE_BACKOFF_FACTOR=int(os.getenv('PRELUDE_BACKOFF_FACTOR', 30))
PRELUDE_BACKOFF_TOTAL=int(os.getenv('PRELUDE_BACKOFF_TOTAL', 0))


class HttpController(object):
    def __init__(self):
        self._session = requests.Session()
        
        retry = Retry(total=PRELUDE_BACKOFF_TOTAL, backoff_factor=PRELUDE_BACKOFF_FACTOR, status_forcelist=[ 429 ])

        self._session.mount('http://', HTTPAdapter(max_retries=retry))
        self._session.mount('https://', HTTPAdapter(max_retries=retry))
