# Brink Framework

[![wercker status](https://app.wercker.com/status/5d9f35bec3b8fff14f91a81e2c957d6a/s/master "wercker status")](https://app.wercker.com/project/byKey/5d9f35bec3b8fff14f91a81e2c957d6a)

## Installation

    $ pip install brink

## Getting started

Getting started is very easy assuming you have Docker installed.

Start RethinkDB like so

    $ docker run -p 8080:8080 -p 28015:28015 -d --name rethink rethinkdb

And then get started with your project like so

    $ brink start-project myproject
    $ cd myproject
    $ brink sync-db
    $ brink run

## Contributing

Get the sources

    $ git clone git@github.com:lohmander/brink.git

create a virtualenv

    $ virtualenv venv
    $ source venv/bin/activate

install Brink

    $ cd brink
    $ pip3 install -e .

start a new project and start working

    $ brink start-project testproj

That's it.

Now whenever you change the framework source code, it'll update in your project.

## Documentation

Full documentation is (will be) available at <https://brinkframework.github.io/brink/>.

