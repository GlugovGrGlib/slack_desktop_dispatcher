#!/usr/bin/env python
# -*- coding: utf-8 -*-

import views


def setup_routes(app):
    app.router.add_get('/', views.index)
    app.router.add_post('/', views.interact)
    app.router.add_get('/send_message', views.send_msg)
    app.router.add_post('/send_event', views.event_processor)
