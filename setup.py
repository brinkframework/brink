from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="brink",
    version="0.3.0",
    description="A simple real time web framework based on\
            aiohttp and RethinkDB.",
    long_description=long_description,
    url="https://github.com/lohmander/brink",
    author="CH Lohmander",
    author_email="hannes@lohmander.me",
    license="BSD-3",

    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: BSD License",

        "Programming Language :: Python :: 3.6",
    ],

    keywords="sample setuptools development",

    packages=find_packages(exclude=["contrib", "docs", "tests"]),

    install_requires=["aiohttp", "aiohttp_autoreload",
                      "rethinkdb", "inflection", "pycolor"],

    setup_requires=["pytest-runner"],
    tests_require=["pytest=3.0.5", "pytest-asyncio"],

    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },

    scripts=["bin/brink"],
)
