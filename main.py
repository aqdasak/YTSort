from googleapiclient.discovery import build, Resource
import os

from config import config
from my_io import input_in_range, print_info, non_empty_input, print_warning
from renaming_helper import RenamingHelper
from cache_manager import CacheManager
from youtube import YTPlaylist, Youtube, YTChannel


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


def get_playlist_id_from_cache(cache: CacheManager):
    playlist_cache_unit = cache.local_playlist_cache.list()[0]
    print_info(
        f"Playlist: \"{playlist_cache_unit['title']}\" found in {os.path.join(os.path.basename(config['local_cache']),'playlist.json')}.")
    return playlist_cache_unit['id']


def get_playlist_id_from_youtube(cache: CacheManager, yt_resource: Resource):
    channel_id = get_channel_id(cache, yt_resource)
    channel = YTChannel(yt_resource, channel_id)
    channel.fetch_playlists()
    channel.print_playlists()
    playlist_cache_unit = channel.select_playlist(
        int(input_in_range('Select playlist: ', 1, channel.total_playlists+1)))
    cache.update_playlist_cache(playlist_cache_unit)
    return playlist_cache_unit['id']


def get_channel_id(cache: CacheManager, yt_resource: Resource):
    def get_from_yt(user_input):
        youtube = Youtube(yt_resource)
        youtube.search_channel(user_input)
        youtube.print_channels()
        return youtube.select_channel(int(input_in_range('Select channel: ', 1, youtube.total_channels+1)))

    if cache.is_local_channel_cache_available():
        channel_cache_unit = cache.local_channel_cache.list()[0]
        print_info(
            f"Channel {channel_cache_unit['title']} found in {os.path.join(os.path.basename(config['local_cache']),'channel.json')}.")

    elif cache.is_shared_channel_cache_available():
        cache.shared_channel_cache.print()
        user_input = non_empty_input(
            'Select or enter channel name to search on youtube: ')
        if user_input.isdigit():
            channel_cache_unit = cache.shared_channel_cache.list()[
                int(user_input) - 1]
        else:
            channel_cache_unit = get_from_yt(user_input)

    else:
        user_input = non_empty_input('Search channel on youtube: ')
        channel_cache_unit = get_from_yt(user_input)

    cache.update_channel_cache(channel_cache_unit)
    cache.save_shared_channel_cache()
    return channel_cache_unit['id']


def rename(renaming_helper: RenamingHelper, cache: CacheManager):
    renaming_helper.generate_rename_dict()

    if renaming_helper.is_rename_dict_formed():
        cache.save()
        renaming_helper.dry_run()

        print('\n')
        confirm = non_empty_input(
            "This can't be undone. Are you sure to rename?(y/n) : ").lower()
        print()
        if confirm == "y" or confirm == "yes":
            renaming_helper.start_batch_rename()
        else:
            print("Nothing renamed")
    else:
        print_info(
            '\nFiles already have serial number or match not found in local files and youtube videos.')
        print_info(
            'Check if you have selected correct playlist or clear the cache.')


def main():
    yt_resource = build('youtube', 'v3', developerKey=config['api_key'])
    print_info(f"If you want to ignore some files, add name of those files in {config['exceptions_file']}"
               f" in the same folder in which files to be renamed are present.")
    files = ls()
    exceptions = get_exceptions()

    cache = CacheManager(config)
    if cache.is_local_playlist_cache_available():
        playlist_id = get_playlist_id_from_cache(cache)
    else:
        playlist_id = get_playlist_id_from_youtube(cache, yt_resource)

    playlist = YTPlaylist(yt_resource, playlist_id)
    playlist.fetch_videos()
    playlist.print_videos()
    remote_serial_dict = playlist.get_videos_serial()

    print()

    renaming_helper = RenamingHelper(
        remote_serial_dict, files, exceptions, character_after_serial=config['character_after_serial'])
    rename(renaming_helper, cache)


if __name__ == '__main__':
    try:
        main()
    except:
        print_warning('Error occured.\nPlease check your internet connection.')
