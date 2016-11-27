from aiohttp import web

from brink.serialization import json_dumps
from brink.exceptions import HTTPBadRequest


class WebSocketResponse(web.WebSocketResponse):

    def send_json(self, json, *args, **kwargs):
        super().send_json(json, *args, dumps=json_dumps, **kwargs)


def __handler_wrapper(handler):
    async def new_handler(request):
        status, data = await handler(request)
        return web.json_response(data, status=status, dumps=json_dumps)
    return new_handler


def __ws_handler_wrapper(handler):
    async def new_handler(request):
        ws = WebSocketResponse()
        await ws.prepare(request)
        await handler(request, ws)
        return ws
    return new_handler
