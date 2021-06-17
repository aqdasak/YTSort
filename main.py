from googleapiclient.discovery import build, Resource
import os

from config import config
from renaming_helper import RenamingHelper

from cache_manager import CacheManager
from youtube import Youtube, YTChannel


def info():
    print(
        f"# If you want to ignore some files, add name of those files in {config['exceptions_file']} in the same folder in which "
        f"files to be renamed are present (or move them in another folder).\n"
    )


def ls():
    # print("Input the path of the folder that contains the files to be renamed or press enter if its current folder.")
    # path = input()
    # if path:
    #     os.chdir(path)
    return os.listdir()


def get_exceptions():
    exceptions = [config['exceptions_file'], config['local_cache'],
                  os.path.basename(__file__)]
    try:
        with open(config['exceptions_file']) as f:
            exceptions.append(f.read().split("\n"))
    except:
        print("No file ignored\n")
    return exceptions


def get_channel_id(yt_resource: Resource):
    def get_from_yt(user_input):
        youtube = Youtube(yt_resource)
        youtube.search_channel(user_input)
        youtube.print_channels()
        return youtube.select_channel(int(input('Select: ')))

    cache = CacheManager(config)
    # if cache.is_local_cache_integrated():
    if cache.is_local_cache_available():
        channel_with_id = cache.local_cache.list()[0]

    # elif cache.is_shared_cache_integrated():
    elif cache.is_shared_cache_available():
        cache.shared_cache.print_channels()
        user_input = input(
            'Select or enter channel name to search on youtube: ')
        if user_input.isdigit():
            channel_with_id = cache.shared_cache.list()[
                int(user_input) - 1]
        else:
            channel_with_id = get_from_yt(user_input)

    else:
        user_input = input('Search channel on youtube: ')
        channel_with_id = get_from_yt(user_input)

    cache.update_cache(channel_with_id)
    cache.save()
    return channel_with_id['channel_id']


def get_videos_serial(channel: YTChannel):
    channel.fetch_playlists()
    channel.select_playlist(int(input('Select from the above playlists: ')))
    channel.generate_videos_serial()
    return channel.get_videos_serial()


def rename(renaming_helper: RenamingHelper):
    renaming_helper.generate_rename_dict()

    if renaming_helper.is_rename_dict_formed():
        renaming_helper.dry_run()

        confirm = input(
            "\n\nThis can't be undone. Are you sure to rename?(y/n) : ").lower()
        print()
        if confirm == "y" or confirm == "yes":
            renaming_helper.start_batch_rename()
        else:
            print("Nothing renamed")
    else:
        print('\nFiles already have serial number or match not found in local files and youtube videos.')
        print('Check if you have selected correct playlist.')


def main():
    yt_resource = build('youtube', 'v3', developerKey=config['api_key'])
    info()
    files = ls()
    exceptions = get_exceptions()

    channel_id = get_channel_id(yt_resource)

    channel = YTChannel(yt_resource, channel_id)
    remote_serial_dict = get_videos_serial(channel)

    print()

    renaming_helper = RenamingHelper(
        remote_serial_dict, files, exceptions, character_after_serial=config['character_after_serial'])
    rename(renaming_helper)


if __name__ == '__main__':
    main()
