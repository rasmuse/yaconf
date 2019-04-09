# yaconf

yet another configuration library

## Features

No frills, no fuss:

```python
import yaconf

conf = yaconf.get_file_reader('myapp')
conf.load()

# reading from .myappconf if available, then ~/.config/myapp/.myappconf
conf['ready to go']
conf.get('ready to go', default='fallback')
```

Add another configuration source:

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

* Python 3.6+ and no external dependencies.
* Single file implementation: Import the package or just copy
* Use any configuration source: any function that returns a `dict` will do.
* Reads JSON files by default, but `configparser` or any other parser can be dropped in with a keyword argument.
* Hierarchical configuration: Look for configuration keys in one config source after another, e.g.,
    - first check `.myappconf` file,
    - then `~/.config/myapp/.myappconf`,
    - finally fall back on defaults.
* Sane defaults for config file paths:
    - `~/.config/myapp/.myappconf` on Linux and MacOS
    - `%LOCALAPPDATA%\myapp\.myappconf` on Windows


## Develop mode

```
virtualenv -p python3.6 ~/.virtualenvs/yaconf
source ~/.virtualenvs/yaconf/bin/activate
pip install -r requirements_dev.txt
pip install -e .
```

## License

Free software: MIT license

## Credits

This package was created with [Cookiecutter][1] and the [`audreyr/cookiecutter-pypackage`][2] project template.

[1] https://github.com/audreyr/cookiecutter
[2] https://github.com/audreyr/cookiecutter-pypackage
