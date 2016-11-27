import rethinkdb as r
from inflection import tableize

from brink.db import conn
from brink.object_manager import ObjectManager
from brink.fields import Field
from brink.exceptions import (
    UndefinedSchema, UnexpectedDbResponse, ValidationError)


class ModelMeta(object):

    def __init__(self):
        self.fields = {}

    def add_field(self, name, field):
        self.fields[name] = field


class ModelBase(type):

    def __new__(cls, name, bases, attrs):
        super_new = super().__new__

        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        new_attrs = {}
        meta_attrs = ModelMeta()
        meta_attrs.add_field("id", Field(pk=True))

        for attr, val in attrs.items():
            if isinstance(val, Field):
                meta_attrs.add_field(attr, val)
            else:
                new_attrs[attr] = val

        new_cls = super_new(cls, name, bases, new_attrs)
        table_name = tableize(name)

        setattr(new_cls, "_meta", meta_attrs)
        setattr(new_cls, "objects", ObjectManager(new_cls, table_name))
        setattr(new_cls, "table_name", table_name)

        return new_cls

    def __getattr__(self, attr):
        return getattr(self.objects, attr)


class Model(object, metaclass=ModelBase):
    """
    Model is to be subclassed by all application models. An arbitrary
    dictionary can be provided upon initialization like so

    ``Model({"key": "value"})``

    which would be the equivalent of this

    ``Model().wrap({"key": "value"})``
    """

    def __init__(self, **kwargs):
        self._state = {}
        self.wrap(kwargs)

    def __json__(self):
        data = {}

        for name, field in self.fields:
            try:
                if field.hidden:
                    continue

                data[name] = field.show(self._state[name])
            except KeyError:
                continue

        return data

    def __setattr__(self, attr, value):
        if attr in [key for key, _ in self.fields]:
            self._state[attr] = self._meta.fields[attr].validate(value)
            print(attr, self._state[attr])
        else:
            super().__setattr__(attr, value)

    def __getattr__(self, attr):
        try:
            return self._state[attr]
        except KeyError:
            raise AttributeError(attr)

    @property
    def fields(self):
        """
        Provides an iterable for all model fields.
        """
        for attr, value in self._meta.fields.items():
            if isinstance(value, Field):
                yield attr, value

    @property
    def __db_repr(self):
        data = {}

        for key, field in self.fields:
            if field.pk:
                continue

            data[key] = field.treat(self._state[key])

        return data

    def wrap(self, data):
        """
        Wraps and consumes an arbitrary dictionary into the model.
        """
        for name, field in self.fields:
            try:
                self._state[name] = data[name]
            except KeyError:
                self._state[name] = None

    def validate(self):
        """
        Validates all field values for the model.
        """

        errors = {}

        for name, field in self.fields:
            try:
                field.validate(self._state.get(name))
            except Exception as e:
                errors[name] = e

        if len(errors) is not 0:
            raise Exception(errors)

        return True

    async def save(self):
        """
        Persists the model to the database. If the model holds no primary key,
        a new one will automatically created by RethinkDB. Otherwise it will
        overwrite the current model persisted to the database.
        """

        if hasattr(self, "before_save"):
            self.before_save()

        query = r.table(self.table_name)

        if self._state.get("id"):
            query = query \
                .get(self._state.get("id")) \
                .replace(self.__db_repr, return_changes=True)
        else:
            query = query \
                .insert(self.__db_repr, return_changes=True)

        resp = await query.run(await conn.get())

        try:
            changes = resp["changes"]

            if len(changes) > 0:
                self.wrap(resp["changes"][0]["new_val"])
        except KeyError:
            raise UnexpectedDbResponse()

        return self

    async def delete(self):
        """
        Deletes the model from the database.
        """
        await r.table_name(self.table_name) \
            .get(self.id) \
            .delete() \
            .run(await conn.get())
