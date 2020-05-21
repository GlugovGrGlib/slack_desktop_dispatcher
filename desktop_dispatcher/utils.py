#!/usr/bin/env python
# -*- coding: utf-8 -*-

import trafaret as T


TRAFARET = T.Dict({
    T.Key('database'):
        T.Dict({
            'db_driver': T.String(),
            'database': T.String(),
            'user': T.String(),
            'password': T.String(),
            'host': T.String(),
            'port': T.Int(),
            'minsize': T.Int(),
            'maxsize': T.Int(),
            'retry_limit': T.Int(),
            'retry_interval': T.Int(),
            'ssl': T.ToBool(),
            'echo': T.ToBool(),
        }),
    T.Key('host'): T.String(),
    T.Key('port'): T.Int(),
})
