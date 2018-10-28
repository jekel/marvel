from aiohttp import web
from aiohttp.web_response import json_response
from project.client import MarvellClient

routes = web.RouteTableDef()


class Marvell:
    def __init__(self):
        self.client = MarvellClient()

    async def get_char_info(self, name):
        search_result = await self.client.characters(name)
        if not search_result:
            raise web.HTTPNotFound

        character = search_result[0]
        comics = await self.client.characters_comics(character['id'], orderby=['onsaleDate'], limit=12)
        events = await self.client.characters_events(character['id'], orderby=['startDate'], limit=12)

        creators = set()
        for comic in comics:
            creators |= set([author['name'] for author in comic['creators']['items']])

        del character['series']
        del character['stories']
        del character['comics']

        character['comics'] = comics
        character['events'] = events
        character['creators'] = list(map(str, creators))

        return character


async def index(request):
    return web.Response(text='use /%NAME% to search for')


async def search(request):
    name = request.match_info['name']
    m = Marvell()
    c = await m.get_char_info(name)

    return json_response(c)



