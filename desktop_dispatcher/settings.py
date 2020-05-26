#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import pathlib

from trafaret_config import commandline
from utils import TRAFARET


BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'add_dev.yaml'


def get_config(argv=None) -> dict:
    ag = argparse.ArgumentParser()
    commandline.standard_argparse_options(
        ag,
        default_config=DEFAULT_CONFIG_PATH
    )

    # ignore unknown options
    options, unknown = ag.parse_known_args(argv)

    config = commandline.config_from_options(options, TRAFARET)
    return config
