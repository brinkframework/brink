from aiohttp import web
from brink.config import config
from brink.db import conn
from brink.handlers import __handler_wrapper, __ws_handler_wrapper
from brink.utils import resolve_func
from brink.cli import print_globe, print_info
import importlib
import aiohttp_autoreload
import logging


def run_server(conf):
    for cfg in vars(conf):
        if cfg[:2] != "__":
            config.set(cfg, getattr(conf, cfg))

    # Setup database config for later use
    conn.setup(config.get("DATABASE", {}))

    # Resolve middleware
    middleware = [resolve_func(func) for
                  func in config.get("MIDDLEWARE", [])]

    server = web.Application(middlewares=middleware)
    logger = logging.getLogger("brink")

    # Iterate over all installed apps and add their routes
    for app in config.get("INSTALLED_APPS", []):
        __load_app(server, app)

    # Enable source code auto reload on change only if DEBUG is enabled
    if config.get("DEBUG"):
        aiohttp_autoreload.add_reload_hook(
            lambda: print_info("Detected code change. Reloading...",
                               spaced=True))

        aiohttp_autoreload.start()

        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)

    server.make_handler(access_log=logger)
    port = config.get("PORT", 8888)
    print_globe("Server listening on port %s\n" % port)
    web.run_app(server, port=port, print=lambda *args: None)


def __load_app(server, package):
    urls = importlib.import_module("%s.urls" % package)

    for url in urls.urls:
        __add_route(server, url, package)


def __add_route(server, url, package):
    (method, route, handler) = url
    handler_wrapper = __ws_handler_wrapper if method == "WS" \
        else __handler_wrapper

    try:
        handler_func = resolve_func(handler)
    except ModuleNotFoundError:
        handler_func = resolve_func("%s.%s" % (package, handler))

    handler_func = handler_wrapper(handler_func)

    if method == "GET" or method == "WS":
        server.router.add_get(route, handler_func)
    elif method == "POST":
        server.router.add_post(route, handler_func)
    elif method == "PUT":
        server.router.add_put(route, handler_func)
    elif method == "PATCH":
        server.router.add_patch(route, handler_func)
    elif method == "DELETE":
        server.router.add_delete(route, handler_func)
