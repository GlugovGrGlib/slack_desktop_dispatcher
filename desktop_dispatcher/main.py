#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web
from sqlalchemy.engine.url import URL

from routes import setup_routes
from models import db
from settings import get_config


async def init_app(argv=None) -> web.Application:
     app = web.Application(middlewares=['db'])

     config = get_config(argv)
     app['config'] = config

     db.init_app(app,
                 dict(
                    dsn=URL(
                        drivername=config['database']['db_driver'],
                        database=config['database']['database'],
                        username=config['database']['user'],
                        password=config['database']['password'],
                        host=config['database']['host'],
                        port=config['database']['port'],
                    ),
                    echo=config['database']['echo'],
                    min_size=config['database']['minsize'],
                    max_size=config['database']['maxsize'],
                    ssl=config['database']['ssl'],
                    retry_limit=config['database']['retry_limit'],
                    retry_interval=config['database']['retry_interval'],
                 ))

     # aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('desktop_dispatcher', 'templates'))

     # setup routes, middlewares and db
     setup_routes(app)

     return app


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    app = init_app(argv)

    config = get_config(argv)
    web.run_app(app,
                host=config['host'],
                port=config['port'])


if __name__ == '__main__':
    main(sys.argv[1:])
