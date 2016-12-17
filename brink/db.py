import rethinkdb as r

from brink.utils import get_config


class Connection(object):
    """
    Connection provides an instance of the rethinkdb connection object.
    """

    def __init__(self):
        self.config = {}
        self.connection = None

    def setup(self, config):
        """
        Setups the database configuartion and sets the RethinkDB loop type to
        asyncio to be compatible with aiohttp.
        """
        r.set_loop_type("asyncio")
        self.config = config

    async def get(self):
        self.connection = self.connection or await r.connect(
            host=self.config.get("host", "localhost"),
            db=self.config.get("db", "test"),
            port=self.config.get("port", 28015)
        )

        return self.connection

    async def close(self):
        conn = await self.get()
        conn.close()
        self.connection = None

conn = Connection()


def get_sync_conn():
    config = get_config()
    return r.connect(**config.DATABASE or {})


def sync_model(model):
    try:
        r.table_create(model.table_name).run(get_sync_conn())
        return "Created table `%s`" % model.table_name
    except r.ReqlOpFailedError as e:
        if "already exists" in e.message:
            return "Table `%s` already exists" % model.table_name
        else:
            raise Exception("An unexpected error occured")
