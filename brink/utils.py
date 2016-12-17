import importlib


def resolve_func(func_string):
    module_name, func_name = func_string.rsplit(".", 1)
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)

    if not func:
        raise ImportError(name=func_name, path=func_string)

    return func


def get_config():
    conf = importlib.import_module("config")
    return conf


def get_app_models(app):
    # TODO: Fix ugly workaround
    from brink.models import Model, ModelBase
    module_name = "%s.models" % app
    module = importlib.import_module(module_name)
    return [model for _, model in module.__dict__.items()
            if isinstance(model, ModelBase) and
            model is not Model and
            model.__module__ == module_name]
