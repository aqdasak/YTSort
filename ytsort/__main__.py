import click
import os
from googleapiclient.discovery import build, Resource

from ytsort.config import config
from ytsort.data_store import DataStore
from ytsort.my_io import input_in_range, non_empty_getpass, print_heading, print_info, non_empty_input, print_warning, take_input
from ytsort.renaming_helper import RenamingHelper
from ytsort.cache_manager import CacheManager
from ytsort.youtube import YTPlaylist, Youtube, YTChannel


def get_exceptions():
    exceptions = [config['exceptions_file'], config['local_cache'],
                  os.path.basename(__file__)]
    try:
        with open(config['exceptions_file']) as f:
            exceptions.append(f.read().split("\n"))
    except Exception:
        print("No file ignored\n")
    return exceptions


def get_playlist_id_from_cache(cache: CacheManager):
    playlist_cache_unit = cache.local_playlist_cache.list()[0]
    print_info(
        f"Playlist: \"{playlist_cache_unit['title']}\" found in cache.")
    inp = take_input('Is the playlist correct?(n if no): ').lower()
    if inp in ('n', 'no'):
        cache.delete_local_playlist_cache()
        print()
        return None
    return playlist_cache_unit['id']


def print_and_select_playlist(playlists: DataStore, warning: str = '') -> dict[str, str]:
    """
    Print the given playlists and take user input to select from the available playlists.
    If user inputs a number the playlist corresponding to that serial number will be selected.
    If user inputs a string, it will select only those playlists which contains the input as the substring of the playlist. The function will be run recursively with only those playlists.

    Parameters
    ----------
    playlists: DataStore

    warning: str
        Give warning if previous input was wrong. `warning` contains the warning message

    Return
    ------
    : dict[str,str]
        Dictionary of type {'title':title,'id':id}
    """

    if warning:
        print_warning(warning)
    else:
        playlists.print()

    user_input = non_empty_input('Select playlist by number or name: ').lower()
    print()

    if user_input.isdigit():
        if 1 <= int(user_input) <= len(playlists):
            # Select and return the playlist if user_input is in correct range
            return playlists[int(user_input)-1]

        # Display warning if user_input is out of range and pass the playlists unchanged
        return print_and_select_playlist(playlists, warning=f'Warning: Input range is [1,{len(playlists)+1})')

    else:
        # Select playlists containing user_input as their title's substring
        temp_playlist = DataStore()
        for playlist in playlists:
            title = playlist['title']
            if user_input in title.lower():
                temp_playlist.update(title, playlist['id'])

        # Rerun the function to take input on matched playlists
        if len(temp_playlist) > 0:
            return print_and_select_playlist(temp_playlist)

    # Display warning if no playlist is matched (and all other cases, if happen) and pass the playlists unchanged
    return print_and_select_playlist(playlists, warning="Didn't match, try again")


def get_playlist_id_from_youtube(cache: CacheManager, yt_resource: Resource):
    channel_id = get_channel_id(cache, yt_resource)
    channel = YTChannel(yt_resource, channel_id)
    channel.fetch_playlists()

    print_heading('<< PLAYLISTS >>')
    playlist_cache_unit = print_and_select_playlist(channel.playlists())

    cache.update_playlist_cache(playlist_cache_unit)
    return playlist_cache_unit['id']


def get_channel_id(cache: CacheManager, yt_resource: Resource):
    def get_from_yt(user_input):
        youtube = Youtube(yt_resource)
        while True:
            youtube.search_channel(user_input)
            if len(youtube.channels()) > 0:
                break
            else:
                user_input = non_empty_input('Not found search again: ')
        youtube.print_channels()
        user_input = int(input_in_range(
            'Select channel: ', 1, len(youtube.channels())+1))
        return youtube.channels()[user_input-1]

    if cache.is_local_channel_cache_available():
        channel_cache_unit = cache.local_channel_cache.list()[0]
        print_info(
            f"Channel: \"{channel_cache_unit['title']}\" found in cache.")
        inp = take_input('Is the channel correct?(n if no): ').lower()
        if inp in ('n', 'no'):
            cache.delete_local_channel_cache()
            print()
            return get_channel_id(cache, yt_resource)

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
        print_info('\nFiles may have been skipped if not present in YouTube playlist or already have serial number prefixed to it or the owner may have renamed the video on YouTube.\n')

        confirm = non_empty_input(
            "This can't be undone. Are you sure to rename?(y if yes): ").lower()
        print()
        if confirm in ('y', 'yes'):
            renaming_helper.start_batch_rename()
        else:
            print("Nothing renamed")
    else:
        print_info(
            '\nFiles already have serial number or match not found in local files and youtube videos.')
        print_info(
            'Check if you have selected correct playlist.')


def main():
    yt_resource = build('youtube', 'v3', developerKey=config['api_key'])
    print_info(f"If you want to ignore some files, add name of those files in {config['exceptions_file']}"
               f" in the same folder in which files to be renamed are present.")
    files = os.listdir()
    exceptions = get_exceptions()

    cache = CacheManager(config)
    if cache.is_local_playlist_cache_available():
        playlist_id = get_playlist_id_from_cache(cache)
        if playlist_id is None:
            playlist_id = get_playlist_id_from_youtube(cache, yt_resource)
    else:
        playlist_id = get_playlist_id_from_youtube(cache, yt_resource)

    playlist = YTPlaylist(yt_resource, playlist_id)
    playlist.fetch_videos()

    print_heading('<< VIDEOS IN THE PLAYLIST >>')
    playlist.videos().print()
    remote_serial_dict = playlist.get_videos_serial()

    print()

    renaming_helper = RenamingHelper(
        remote_serial_dict, files, exceptions, character_after_serial=config['character_after_serial'], padded_zero=config['padded_zero'])
    rename(renaming_helper, cache)


@click.command()
@click.option('-c', '--character', help='Character after serial.')
@click.option('-p', '--padded-zero', is_flag=True, help='Padded zero.')
@click.option('-np', '--no-padded-zero', is_flag=True, help='No padded zero.')
def cli(character, padded_zero, no_padded_zero):
    if character is not None:
        config['character_after_serial'] = character

    if padded_zero and not no_padded_zero:
        config['padded_zero'] = True
    elif not padded_zero and no_padded_zero:
        config['padded_zero'] = False
    # else default in config is used

    if config['api_key'] is None:
        config['api_key'] = non_empty_getpass('Please provide api key: ')
        print('You can set your api key to the environment variable YOUTUBE_DATA_API_KEY')

    try:
        main()
    except KeyboardInterrupt:
        print('\nAborted!')
    except Exception:
        print_warning(
            'Error occured.\nPlease check your internet connection or API key.')


if __name__ == '__main__':
    cli()
