import hashlib
import os
import time
from json import JSONDecodeError

import aiohttp

from project.exceptions import NotFoundMarvellException, GenericMarvellException

KEY = os.environ['KEY']
SECRET = os.environ['SECRET']


class MarvellClient:
    API_URL = 'https://gateway.marvel.com:443'
    API_VERSION = 'v1'

    def __init__(self):
        self.conn = aiohttp.TCPConnector()
        self.session = aiohttp.ClientSession(connector=self.conn, connector_owner=False)

    def root_url(self):
        url = '{}/{}'.format(self.API_URL, self.API_VERSION)
        return url

    @staticmethod
    def get_nonce():
        return str(int(time.time() * 1000))

    def sign(self):
        nonce = self.get_nonce()
        msg = '{}{}{}'.format(nonce, SECRET, KEY).encode()
        signed = hashlib.md5(msg).hexdigest()

        signature = {
            'hash': signed,
            'ts': nonce,
            'apikey': KEY
        }
        return signature

    async def call(self, uri, params):
        url = '{}/{}'.format(self.root_url(), uri)

        params = params or {}
        params.update(self.sign())

        async with self.session.get(url, params=params) as response:
            return await self.parse_response(response)

    async def parse_response(self, response):
        url = response.url
        if response.status >= 500:
            response.raise_for_status()
        elif response.status == 404:
            response = await response.text()
            raise NotFoundMarvellException()

        try:
            response = await response.json(content_type='') if response.content else {}
        except (AttributeError, TypeError, JSONDecodeError):
            response = await response.text()
            raise Exception(response)

        if response['code'] != 200:
            # status = response['status']
            raise GenericMarvellException()

        # we assume that there is always collection returned
        res = response['data']['results']
        return res

    async def characters(self, name):
        params = {
            'name': name
        }
        return await self.call('public/characters', params)

    async def characters_comics(self, character_id: int, orderby: list=None, limit=None):
        url = 'public/characters/{}/comics'.format(character_id)
        params = {
            'orderBy': ','.join(orderby) or None,
            'limit': limit
        }
        return await self.call(url, params)

    async def characters_events(self, character_id: int, orderby: list=None, limit=None):
        url = 'public/characters/{}/events'.format(character_id)
        params = {
            'orderBy': ','.join(orderby) or None,
            'limit': limit
        }
        return await self.call(url, params)

    async def creators(self, comics: list=None, events: list=None, orderby: list=None, limit=None):
        params = {
            'orderBy': ','.join(orderby) or None,
            'limit': limit,
            'comics': ','.join([str(c) for c in comics]) if comics else None,
            'events': ','.join([str(e) for e in events]) if events else None
        }
        return await self.call('public/creators', params)
