import os

config = {
    'api_key': os.environ.get('YOUTUBE_DATA_API_KEY'),
    'renaming_folder_path': os.getcwd(),
    'program_folder_path': os.path.dirname(__file__),
    'exceptions_file': 'exceptions.txt',
    'character_after_serial': ')',
    'local_cache': 'channel_id.txt',
    'shared_cache': 'channel.json',
    'cache_indent': 4
}
