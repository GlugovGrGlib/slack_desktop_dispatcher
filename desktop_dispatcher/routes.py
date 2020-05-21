#!/usr/bin/env python
# -*- coding: utf-8 -*-

from views import index


def setup_routes(app):
    app.router.add_get('/', index)
