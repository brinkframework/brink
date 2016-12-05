import importlib
import re

from aiohttp import web

from brink.serialization import json_dumps
from brink.exceptions import HTTPBadRequest
from brink.config import config


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


def __get_url_params(url):
    return re.findall(r"{(.*?)}", url)


async def handle_list_urls(request):
    apps = config.get("INSTALLED_APPS", default=[])
    endpoints = []

    for app in apps:
        try:
            urls = importlib.import_module("%s.urls" % app)

            for (method, url, _) in urls.urls:
                endpoints.append({
                    "method": method,
                    "url": url,
                    "url_params": __get_url_params(url),
                })
        except ModuleNotFoundError as e:
            continue

    return 200, {"data": endpoints}
