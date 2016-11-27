import asyncio


def require_request_model(cls, validate=True):
    """
    Makes a handler require that a request body that map towards the given
    model is provided. Unless the ``validate`` option is set to ``False`` the
    data will be validated against the model's fields.

    The model will be passed to the handler as the last positional argument. ::

        @require_request_model(Model)
        async def handle_model(request, model):
            return 200, model
    """
    def decorator(handler):
        async def new_handler(request, *args, **kwargs):
            body = await request.json()
            model = cls(**body)

            if validate:
                model.validate()

            return await handler(request, model, *args, **kwargs)
        return new_handler
    return decorator


def use_ws_subhandlers(handler):
    """
    Allows the handler to return any number of **subhandlers** that will be
    run in parallel. This makes it much cleaner and easier to write a handler
    that both listens for incoming messages on the socket connection, while
    also watching a changefeed from RethinkDB.

    Example usage ::

        @use_ws_subhandlers
        async def handle_feed(request, ws):
            async def handle_incoming(_, ws):
                async for msg in ws:
                    await Item(value=msg.data).save()

            async def handle_change(_, ws):
                async for item in await Item.changes():
                    ws.send_json(item)

            return [handle_incoming, handle_change]
    """
    async def new_handler(request, ws):
        handlers = await handler(request, ws)
        tasks = [request.app.loop.create_task(h(request, ws))
                 for h in handlers]

        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                task.cancel()

            await ws.close()
    return new_handler
