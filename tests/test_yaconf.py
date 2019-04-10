#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `yaconf` package."""

import pytest

import yaconf


@pytest.fixture
def empty():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    conf = yaconf.get_file_reader('myapp')

    return conf

@pytest.fixture
def basic(empty):

    def get_default_config():
        return {'i': 123, 'b': 'default string'}

    # Add this configuration with lowest priority
    empty.loaders.append(get_default_config)

    empty.load()

    return empty

def test_must_initialize(empty):
    with pytest.raises(yaconf.ConfigError) as excinfo:
        empty['not ready to go']

    assert 'Config not loaded' in str(excinfo.value)

    empty.load()

def test_missing_key(empty):
    empty.load()

    with pytest.raises(KeyError):
        empty['ready to go']

    empty.get('ready to go') # has default value

def test_override(basic):

    def get_top_priority_config():
        return {'b': 'other string'}

    # And this one with highest priority
    basic.loaders.insert(0, get_top_priority_config)

    assert basic['i'] == 123
    assert basic['b'] == 'default string'

    # To include the new configuration source
    basic.load()

    assert basic['i'] == 123
    assert basic['b'] == 'other string'

def test_mapping(basic):
    d = dict(basic)
    assert d == {'i': 123, 'b': 'default string'}

def test_modify_added(basic):
    assert basic['i'] == 123
    assert basic['b'] == 'default string'

    def modify(d):
        d['i'] += 3
        del d['b']
        d['x'] = 'new'

    basic.modify = modify

    assert dict(basic) == {'i': 123, 'b': 'default string'}

    basic.load()

    assert dict(basic) == {'i': 126, 'x': 'new'}
