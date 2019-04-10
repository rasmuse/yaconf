# yaconf

yet another Python configuration library

## Features

No frills, no fuss:

* Python 3.6+ and no external dependencies.
* Single file implementation: Import the package or just copy `yaconf.py` into your project.
* Use any configuration source: any function that returns a `dict` will do.
* Reads JSON files by default, but `configparser` or any other parser can be dropped in with a keyword argument.
* Hierarchical configuration: Look for configuration keys in one config source after another, e.g.,
    - first check `.myappconf` file,
    - then `~/.config/myapp/.myappconf`,
    - finally fall back on defaults.
* Sane defaults for config file paths:
    - `~/.config/myapp/.myappconf` on Linux and MacOS
    - `%LOCALAPPDATA%\myapp\.myappconf` on Windows
* Optionally register a modifier function to arbitrarily change values after loading (e.g., change datatypes, check consistency, etc).

## Examples

### Basic setup

```python
import yaconf

conf = yaconf.get_file_reader('myapp')
conf.load()

# reading from .myappconf if available, then ~/.config/myapp/.myappconf
conf['ready to go']
conf.get('ready to go', default='fallback')
```

### Add more configuration sources

```python
def get_default_config():
    return {'i': 123, 'b': 'default string'}

# Add this configuration with lowest priority
conf.loaders.append(get_default_config)

def get_top_priority_config():
    return {'b': 'other string'}

# And this one with highest priority
conf.loaders.push(get_top_priority_config)

# To include the new configuration source
conf.load()
assert conf['i'] == 123
assert conf['b'] == 'other string'

```

### The ConfigReader is a Mapping

```python
assert dict(conf) == {'i': 123, 'b': 'other string'}
```


### Add a modify function

```python
def modify(d):
        d['i'] += 3
        del d['b']
        d['x'] = 'new'

conf.modify = modify
conf.load()

assert dict(conf) == {'i': 126, 'x': 'new'}
```

## License

Free software: MIT license

## Credits

This package was created with [Cookiecutter][1] and the [`audreyr/cookiecutter-pypackage`][2] project template.

[1]: https://github.com/audreyr/cookiecutter
[2]: https://github.com/audreyr/cookiecutter-pypackage
