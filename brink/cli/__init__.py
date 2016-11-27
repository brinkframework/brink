from pycolor import print_color

from brink.cli import emojis


def print_msg(*args, spaced=False, indent=0, **kwargs):
    msg = (" " * indent) + " ".join(args).strip()

    if spaced:
        msg = "\n%s\n" % msg

    print_color(msg, **kwargs)


def print_success(*args, **kwargs):
    print_msg(emojis.check, *args, **kwargs, fg_color="green")


def print_error(*args, **kwargs):
    print_msg(emojis.error, *args, **kwargs, fg_color="white", bg_color="red")


def print_globe(*args, **kwargs):
    print_msg(emojis.globe, *args, **kwargs, fg_color="black")


def print_info(*args, **kwargs):
    print_msg(*args, **kwargs, fg_color="lightgray")


def print_monkey(*args, **kwargs):
    print_msg(emojis.monkey, *args, **kwargs)


def print_docker(*args, **kwargs):
    print_msg(emojis.whale, *args, **kwargs)


def print_done(*args, **kwargs):
    if len(args) == 0:
        args = ["Done"]

    print_msg(emojis.thumb, *args, **kwargs)
