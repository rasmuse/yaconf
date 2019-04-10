# -*- coding: utf-8 -*-

import sys
import os
import json
from pathlib import Path
import collections
from types import MappingProxyType as frozendict
from typing import (
    Callable,
    Sequence,
    Mapping,
    Any,
    Union,
    Optional,
    List,
    )

PathLike = Union[Path, str]
ConfigMapping = Mapping[Any, Any]
Decoder = Callable[[str], ConfigMapping]
Loader = Callable[[], ConfigMapping]
Modifier = Callable[[ConfigMapping], Any]


class ConfigReader(collections.abc.Mapping):
    loaders: List[Loader]
    modify: Modifier

    def __init__(self, loaders: Sequence[Loader]):
        self.loaders = list(loaders)
        self.modify = None

    def _check_loaded(self):
        if not hasattr(self, '_config'):
            raise ConfigError('Config not loaded. Call load() before reading.')

    def load(self):
        self._config = {}
        for loader in reversed(self.loaders):
            self._config.update(loader())

        if self.modify is not None:
            self.modify(self._config)

    def get(self, *args, **kwargs):
        self._check_loaded()
        return self._config.get(*args, **kwargs)

    def __getitem__(self, key):
        self._check_loaded()
        return self._config[key]

    def __iter__(self):
        yield from self._config

    def __len__(self):
        return len(self._config)

    def __repr__(self):
        loader_strings = map(str, self.loaders)
        return f'{type(self).__name__}([{", ".join(loader_strings)}])'


_DEFAULT_CONFIG_FILENAME = '.{app_name}conf'


def get_default_config_dir(app_name: str) -> str:
    if sys.platform == 'win32':
        return os.path.expandvars(rf'%LOCALAPPDATA%\{app_name}')

    return os.path.expanduser(f'~/.config/{app_name}/')


def get_default_paths(
        app_name: str,
        filename: Optional[PathLike] = None
        ) -> Sequence[PathLike]:

    if filename is None:
        filename = _DEFAULT_CONFIG_FILENAME.format(app_name=app_name)

    user_config_dir = get_default_config_dir(app_name)

    paths = [
        filename,  # first check local directory
        os.path.join(user_config_dir, filename)  # then user config directory
        ]

    return paths


class ConfigError(Exception):
    pass


class FileLoader:
    def __init__(self, path, decoder):
        self.path = path
        self.decoder = decoder

    def __call__(self) -> ConfigMapping:
        try:
            with open(self.path) as f:
                s = f.read()
            self.decoder(s)
            return frozendict(self.decoder(s))
        except FileNotFoundError:
            return {}
        except Exception as e:
            raise ConfigError(f'error decoding config file {self.path}') from e

    def __repr__(self):
        return f"{type(self).__name__}('{self.path}')"


def get_file_reader(
        app_name: str,
        filename: Optional[PathLike] = None,
        decoder: Decoder = json.loads
        ) -> ConfigReader:

    paths = get_default_paths(app_name, filename)

    loaders = [FileLoader(path, decoder) for path in paths]

    return ConfigReader(loaders)
