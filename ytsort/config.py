"""
Get and set config.

Create .ytsort_cache/config.json if not present.
"""

# 'character_after_serial' and 'padded_zero' can be changed from command line options.
# 'api_key' can be provided while running. Default config can be changed by command line.

import json
import os

from ytsort.my_io import non_empty_input, print_info


def get_factory_defaults() -> dict[str, str | int | bool | None]:
    return {
        'api_key': None,
        'character_after_serial': ")",
        'padded_zero': False
    }


def create_config_json():
    config = get_factory_defaults()
    defaults = os.path.join(os.path.dirname(__file__),
                            '.ytsort_cache/config.json')
    with open(defaults, 'w') as f:
        json.dump(config, f, indent=2)


def get_config() -> dict[str, str | int | bool | None]:
    defaults = os.path.join(os.path.dirname(__file__),
                            '.ytsort_cache/config.json')
    with open(defaults) as f:
        config = json.load(f)

    config.update({
        'exceptions_file': '.ytsignore',
        'cache_indent': 2,
        'local_cache': os.path.join(os.getcwd(), '.ytsort_cache/'),
        'shared_cache': os.path.join(os.path.dirname(__file__), '.ytsort_cache/'),
    })

    if config['api_key'] is None:
        config['api_key'] = os.environ.get('YOUTUBE_DATA_API_KEY')

    return config


def change_default_config():
    """
    Config wizard

    Allows the user to change the defaults to be used in config.
    """

    config_json = os.path.join(os.path.dirname(
        __file__), '.ytsort_cache/config.json')
    with open(config_json, 'r+') as f:
        defaults = json.load(f)

        factory_default = get_factory_defaults()

        print_info("Input '.' to skip or '/' to reset to factory default.")
        api_key = non_empty_input(
            'Input API key. Reset to use API key from environment: ').strip()

        # If given more, only take first character of the string
        character_after_serial = non_empty_input(
            "Input character to put after serial numbers or '*' to put no character: ").strip()[:1]
        padded_zero = non_empty_input(
            'Input yes/y to add zero before serial numbers else no/n: ').strip()

        if api_key == '.':
            pass
        elif api_key == '/':
            defaults['api_key'] = factory_default['api_key']
        else:
            defaults['api_key'] = api_key

        if character_after_serial == '.':
            pass
        elif character_after_serial == '/':
            defaults['character_after_serial'] = factory_default['character_after_serial']
        elif character_after_serial == '*':
            defaults['character_after_serial'] = ''
        else:
            defaults['character_after_serial'] = character_after_serial

        padded_zero = padded_zero.lower()
        if padded_zero == '.':
            pass
        elif padded_zero == '/':
            defaults['padded_zero'] = factory_default['padded_zero']
        elif padded_zero in ('y', 'yes'):
            defaults['padded_zero'] = True
        elif padded_zero in ('n', 'no'):
            defaults['padded_zero'] = False

        f.seek(0)
        json.dump(defaults, f, indent=2)
        f.truncate()


shared_cache = os.path.join(os.path.dirname(__file__), '.ytsort_cache/')
if not os.path.exists(shared_cache):
    os.mkdir(shared_cache)

config_json = os.path.join(os.path.dirname(
    __file__), '.ytsort_cache/config.json')
if not os.path.exists(config_json):
    create_config_json()
