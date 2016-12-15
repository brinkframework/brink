def get(route, handler):
    return ("GET", route, handler)


def post(route, handler):
    return ("POST", route, handler)


def put(route, handler):
    return ("PUT", route, handler)


def patch(route, handler):
    return ("PATCH", route, handler)


def delete(route, handler):
    return ("DELETE", route, handler)


def ws(route, handler):
    return ("WS", route, handler)

# TODO: deprecate and remove
GET = get
POST = post
PUT = put
PATCH = patch
DELETE = delete
WS = ws
