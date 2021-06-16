from cache_manager import *
from search_channel import *
from config import config

cache = CacheManager(config)


def get_channel_id(yt_build, program_folder_path, renaming_folder_path):
    def end(channel_with_id):
        channel_id = channel_with_id['channel_id']
        # add_to_channel_json(program_folder_path, channel_with_id)
        # add_to_channel_id_txt(renaming_folder_path, channel_with_id)
        cache.shared_cache = channel_with_id
        cache.local_cache = channel_with_id
        return channel_id

    if is_local_cache_integrated(renaming_folder_path):
        # channel_with_id = read_from_channel_id_txt(renaming_folder_path)
        channel_with_id = cache.local_cache
    else:
        if is_shared_cache_integrated(program_folder_path):
            # channel_with_id_list = read_from_channel_json(program_folder_path)
            channel_with_id_list = cache.shared_cache
            print_channels(channel_with_id_list)
            user_input = input(
                'Select or enter channel name to search on youtube: ')
            if user_input.isdigit():
                channel_with_id = channel_with_id_list[int(user_input) - 1]
            else:
                channel_with_id_list = search_channel_on_youtube(
                    yt_build, user_input)
                print_channels(channel_with_id_list)
                user_input = int(input('Select: '))
                channel_with_id = channel_with_id_list[user_input - 1]
        else:
            user_input = input('Search channel on youtube: ')
            channel_with_id_list = search_channel_on_youtube(
                yt_build, user_input)
            print_channels(channel_with_id_list)
            user_input = int(input('Select: '))
            channel_with_id = channel_with_id_list[user_input - 1]

    return end(channel_with_id)
