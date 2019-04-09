# -*- coding: utf-8 -*-

import sys
import os
import json
import logging
from pathlib import Path
from types import MappingProxyType as frozendict
from typing import (
    Callable,
    Sequence,
    Mapping,
    Any,
    Union,
    Optional,
    )
from collections import OrderedDict
import functools

PathLike = Union[Path, str]
ConfigMapping = Mapping[Any, Any]
Decoder = Callable[[str], ConfigMapping]

class ConfigReader:
    loaders: OrderedDict

    def __init__(self, loaders: OrderedDict):
        self.loaders = loaders
        self._loaded = False

    @property
    def levels(self):
        return self._configs

    def _check_loaded(self):
        if not hasattr(self, '_configs'):
            raise ConfigError('Config not loaded. Call load() before reading.')

    def load(self):
        self._configs = OrderedDict()
        for level, loader in self.loaders.items():
            self._configs[level] = loader()

        self._configs = frozendict(self._configs)

    def get(self, key, default=None):
        self._check_loaded()
        try:
            return self[key]
        except KeyError:
            return default

    def get_level(self, name):
        self._check_loaded()
        return self._configs[name]

    def __getitem__(self, key):
        self._check_loaded()
        for d in self._configs.values():
            if key in d:
                return d[key]

        raise KeyError(f"key '{key}' not in any config dictionary")

    def __repr__(self):
        loader_strings = (
            f"'{name}': {loader}"
            for name, loader in self.loaders.items()
            )

        return f'{type(self).__name__}([{", ".join(loader_strings)}])'


_DEFAULT_CONFIG_FILENAME = '.{app_name}conf'

def get_default_config_dir(app_name: str) -> str:
    if sys.platform == 'win32':
        return path.expandvars(rf'%LOCALAPPDATA%\{app_name}')

    return os.path.expanduser(f'~/.config/{app_name}/')

def get_default_paths(
    app_name: str,
    filename: Optional[PathLike] = None
    ) -> Mapping[str, PathLike]:

    paths = OrderedDict()
    if filename is None:
        filename = _DEFAULT_CONFIG_FILENAME.format(app_name=app_name)

    user_config_dir = get_default_config_dir(app_name)

    paths['local'] = filename
    paths['user'] = os.path.join(user_config_dir, filename)

    return paths


class ConfigError(Exception):
    pass


class FileLoader:
    path: PathLike
    decoder: Decoder

    def __init__(self, path, decoder):
        self.path = path
        self.decoder = decoder

    def __call__(self):
        try:
            with open(self.path) as f:
                s = f.read()
            return frozendict(self.decoder(s))
        except FileNotFoundError:
            return {}
        except Exception as e:
            raise ConfigError(f'error decoding config file at {path}') from e

    def __repr__(self):
        return f"{type(self).__name__}('{self.path}')"


def get_file_reader(
    app_name: str,
    filename: Optional[PathLike] = None,
    decoder: Decoder = json.loads
    ) -> ConfigReader:

    paths = get_default_paths(app_name, filename)
    loaders = OrderedDict()
    for name, path in paths.items():
        loaders[name] = FileLoader(path, decoder)

    return ConfigReader(loaders)
