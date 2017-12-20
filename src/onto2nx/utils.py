# -*- coding: utf-8 -*-

import requests
from requests_file import FileAdapter
from requests.compat import urlparse
import logging

log = logging.getLogger(__name__)


def download(url):
    """Uses requests to download an URL, maybe from a file"""
    session = requests.Session()
    session.mount('file://', FileAdapter())

    try:
        res = session.get(url)
    except requests.exceptions.ConnectionError as e:
        raise e

    res.raise_for_status()

    return res


def get_uri_name(url):
    """Gets the file name from the end of the URL. Only useful for PyBEL's testing though since it looks specifically
    if the file is from the weird owncloud resources distributed by Fraunhofer"""
    url_parsed = urlparse(url)

    url_parts = url_parsed.path.split('/')

    log.info('url parts: %s', url_parts)

    return url_parts[-1]
