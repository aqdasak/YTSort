import os

config = {
    'api_key': os.environ.get('YOUTUBE_DATA_API_KEY'),
    'exceptions_file': 'exceptions.txt',
    'local_cache': os.path.join(os.getcwd(), '.ytsort_cache/'),
    'shared_cache': os.path.join(os.path.dirname(__file__), '.ytsort_cache/'),
    'cache_indent': 4,
    'character_after_serial': ')',
}
