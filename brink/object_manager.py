import rethinkdb as r

from brink.db import conn


class ObjectManager(object):

    def __init__(self, model_cls, table_name):
        self.model_cls = model_cls
        self.table_name = table_name

    def __getattr__(self, attr):
        qs = QuerySet(self.model_cls, self.table_name)
        return getattr(qs, attr)


class QuerySet(object):
    aggregators = ["group", "ungroup", "reduce", "fold", "count", "sum", "avg",
                   "min", "max", "distinct", "contains"]

    def __init__(self, model_cls, table_name):
        self.model_cls = model_cls
        self.query = r.table(table_name)
        self.single = False
        self.returns_changes = False
        self.non_model_res = False

    def __await__(self):
        return self.__run().__await__()

    def __getattr__(self, attr):
        def proxy(*args, **kwargs):
            self.query = getattr(self.query, attr)(*args, **kwargs)

            if attr in self.aggregators:
                self.non_model_res = True

            return self
        return proxy

    async def __run(self):
        res = await self.query.run(await conn.get())
        if self.non_model_res:
            return res
        elif self.single:
            return self.model_cls(**res)
        else:
            return ObjectSet(
                self.model_cls,
                res,
                returns_changes=self.returns_changes
            )

    def get(self, id):
        self.query = self.query.get(id)
        self.single = True
        return self

    def all(self):
        return self

    def changes(self, *args, **kwargs):
        self.query = self.query.changes(*args, **kwargs)
        self.returns_changes = True
        self.single = False
        return self

    async def as_list(self):
        return await (await self).as_list()


class ObjectSet(object):

    def __init__(self, model_cls, cursor, returns_changes=False):
        self.cursor = cursor
        self.model_cls = model_cls
        self.returns_changes = returns_changes

    async def as_list(self):
        return [obj async for obj in self]

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.cursor is None:
            self.cursor = await self.query.run(await conn.get())

        if (await self.cursor.fetch_next()):
            data = await self.cursor.next()

            if self.returns_changes:
                data = data["new_val"]

            model = self.model_cls(**data)

            return model
        else:
            raise StopAsyncIteration
