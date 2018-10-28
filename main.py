from aiohttp import web

from project import rest

rest = rest


if __name__ == '__main__':
    app = web.Application()

    app.router.add_get('/', rest.index)
    app.router.add_get('/{name}', rest.search)

    web.run_app(app)
