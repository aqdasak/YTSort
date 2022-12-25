import click
import os
from googleapiclient.discovery import build, Resource

from ytsort.config import config
from ytsort.data_store import DataStore
from ytsort.my_io import input_in_range, is_int, non_empty_getpass, print_heading, print_info, non_empty_input, print_warning, take_input
from ytsort.renamer import Renamer
from ytsort.cache_manager import CacheManager
from ytsort.youtube import YTPlaylist, Youtube, YTChannel


def get_exceptions() -> list[str]:
    """List of files not to be renamed"""

    exceptions = []
    try:
        with open(config['exceptions_file']) as f:
            exceptions.extend(f.read().split("\n"))
    except Exception:
        pass

    exceptions = [i for i in exceptions if i != '']
    if len(exceptions) > 0:
        print('\nFollowing files will be ignored:')
        for i, file in enumerate(exceptions, start=1):
            print(f"{i}. '{file}'")
    else:
        print('\nNo file ignored.')

    exceptions.extend([config['exceptions_file'], config['local_cache']])
    return exceptions


def print_and_select_playlist(playlists: DataStore) -> dict[str, str]:
    """
    Print the given playlists and take user input to select from the available playlists.
    If user inputs a number the playlist corresponding to that serial number will be selected.
    If user inputs a string, it will select only those playlists which contains the input as the substring of the playlist. The function will be run recursively with only those playlists.

    Parameters
    ----------
    playlists: DataStore
        Collection of playlists from which a playlist is selected by user

    Return
    ------
    : dict[str,str]
        Dictionary of type {'title':title,'id':id}
    """

    def p_a_s_p(original_playlists: DataStore, current_playlists: DataStore, warning: str = '') -> dict[str, str]:
        """
        Helper function

        Parameters
        ----------
        warning: str (Optional)
            Give warning if previous input was wrong. `warning` contains the warning message
        """

        if warning:
            print_warning(warning)
        else:
            current_playlists.print()

        if len(current_playlists) < len(original_playlists):
            print_info("Enter '/' to reset search")

        user_input = non_empty_input(
            'Select playlist by number or search name: ').lower()
        print()

        if is_int(user_input):
            if 1 <= int(user_input) <= len(current_playlists):
                # Select and return the playlist if user_input is in correct range
                return current_playlists[int(user_input)-1]

            # Display warning if user_input is out of range and pass the playlists unchanged
            return p_a_s_p(original_playlists, current_playlists, warning=f'Wrong input: Input range is [1,{len(current_playlists)}]')

        elif user_input == '/':
            # Reset the search
            return p_a_s_p(original_playlists, original_playlists)

        else:
            # Select playlists containing user_input as their title's substring
            temp_playlist = DataStore()
            for playlist in current_playlists:
                title = playlist['title']
                if user_input in title.lower():
                    temp_playlist.update(title, playlist['id'])

            # Rerun the function to take input on matched playlists
            if len(temp_playlist) > 0:
                return p_a_s_p(original_playlists, temp_playlist)

        # Display warning if no playlist is matched (and all other cases, if happen) and pass the playlists unchanged
        return p_a_s_p(original_playlists, current_playlists, warning="Didn't match, try again")

    return p_a_s_p(playlists, playlists)


def get_playlist_id_from_local_cache(cache: CacheManager) -> str | None:
    """
    Fetch playlist cache from local cache and ask user if the playlist is correct or not. If the playlist is correct return playlist's ID else delete local cache and return None.

    Parameters
    ----------
    cache: CacheManager
        CacheManager object

    Returns
    -------
        playlist_id: str
            ID of the YouTube playlist
        None
            If ID is not discarded by user 
    """

    playlist_cache_unit = cache.local_playlist_cache.list()[0]
    print_info(
        f"\nPlaylist: \"{playlist_cache_unit['title']}\" found in cache.")

    inp = take_input('Is the playlist correct?(n if no): ').lower()
    if inp in ('n', 'no'):
        cache.delete_local_playlist_cache()
        print()
        return None

    return playlist_cache_unit['id']


def get_playlist_id_from_youtube(cache: CacheManager, yt_resource: Resource) -> str:
    """
    Fetch playlists from YouTube and return playlist's ID

    Parameters
    ----------
    cache: CacheManager
        CacheManager object
    yt_resource: googleapiclient.discovery.Resource
        Required to access YouTube's Data API

    Returns
    -------
        playlist_id: str
            ID of the YouTube playlist
    """

    channel_id = get_channel_id(cache, yt_resource)
    channel = YTChannel(yt_resource, channel_id)
    channel.fetch_playlists()

    print_heading('<< PLAYLISTS >>')
    playlist_cache_unit = print_and_select_playlist(channel.playlists())

    cache.update_playlist_cache(playlist_cache_unit)
    return playlist_cache_unit['id']


def get_channel_id(cache: CacheManager, yt_resource: Resource) -> str:
    """
    Check Channel ID in local cache, if not found then in shared cache, and then search on YouTube and then returns the Channel ID.

    Parameters
    ----------
    cache: CacheManager
        CacheManager object to manage cache
    yt_resource: googleapiclient.discovery.Resource
        Required to access YouTube's Data API

    Returns
    -------
        channel_id: str
            ID of the YouTube channel
    """

    def get_channel_from_youtube(search_query: str, yt_resource: Resource) -> dict[str, str]:
        """
        Search channels on YouTube, print them, ask user to select among them and return the user selected channel

        Parameters
        ----------
        search_query: str
            Channel name to be searched on YouTube
        yt_resource: googleapiclient.discovery.Resource
            Required to access YouTube's Data API

        Returns
        -------
            channel: dict[str, str]
                YouTube channel dictionary {'title': <title>, 'id': <id>}
        """

        youtube = Youtube(yt_resource)
        while True:
            youtube.search_channel(search_query)
            if len(youtube.channels()) > 0:
                break
            search_query = non_empty_input('Not found search again: ')

        youtube.print_channels()
        select = int(input_in_range(
            'Select channel: ', 1, len(youtube.channels())))
        return youtube.channels()[select-1]

    if cache.is_local_channel_cache_available():
        channel_cache_unit = cache.local_channel_cache.list()[0]
        print_info(
            f"Channel: \"{channel_cache_unit['title']}\" found in cache.")

        inp = take_input('Is the channel correct?(n if no): ').lower()
        if inp in ('n', 'no'):
            # If the channel in local cache is not correct then delete it from local cache and rerun the `get_channel_id()` function
            cache.delete_local_channel_cache()
            print()
            return get_channel_id(cache, yt_resource)

    elif cache.is_shared_channel_cache_available():
        cache.shared_channel_cache.print()
        user_input = non_empty_input(
            'Select or enter channel name to search on youtube: ')

        # If the user_input is digit and in correct range then select from the given channels else search it on YouTube
        if is_int(user_input):
            # Select the channel if user_input is in correct range
            if 1 <= int(user_input) <= len(cache.shared_channel_cache):
                channel_cache_unit = cache.shared_channel_cache.list()[
                    int(user_input) - 1]

            # Display warning if user_input is out of range and rerun the function
            else:
                print_warning(
                    f'\nWrong input: Input range is [1,{len(cache.shared_channel_cache)}]')
                return get_channel_id(cache, yt_resource)
        else:
            channel_cache_unit = get_channel_from_youtube(
                user_input, yt_resource)

    else:
        user_input = non_empty_input('Search channel on youtube: ')
        channel_cache_unit = get_channel_from_youtube(
            user_input, yt_resource)

    cache.update_channel_cache(channel_cache_unit)
    cache.save_shared_channel_cache()
    return channel_cache_unit['id']


def rename(renamer: Renamer, cache: CacheManager):
    """
    Rename the files using `renamer`.

    Parameters
    ----------
    renamer: Renamer
        Contains all the information and logic required to rename files.
    cache: CacheManager
        CacheManager object to manage cache
    """

    renamer.generate_rename_dict()

    if renamer.is_rename_dict_formed():
        cache.save()
        renamer.dry_run()
        print_info('\nFiles may have been skipped if not present in YouTube playlist or already have serial number prefixed to it or the owner may have renamed the video on YouTube.\n')

        confirm = non_empty_input(
            "This can't be undone. Are you sure to rename?(y if yes): ").lower()
        print()
        if confirm in ('y', 'yes'):
            renamer.start_batch_rename()
        else:
            print("Nothing renamed")
    else:
        print_info(
            '\nFiles already have serial number or match not found in local files and youtube videos.')
        print_info(
            'Check if you have selected correct playlist.')


def main():
    yt_resource = build('youtube', 'v3', developerKey=config['api_key'])
    print_info(f"\nIf you want to ignore some files, add name of those files in {config['exceptions_file']}"
               f" in the same folder in which files to be renamed are present.")
    files = os.listdir()
    exceptions = get_exceptions()

    cache = CacheManager(config)
    if cache.is_local_playlist_cache_available():
        playlist_id = get_playlist_id_from_local_cache(cache)
        if playlist_id is None:
            # playlist_id is None if the user discarded the availaible id
            playlist_id = get_playlist_id_from_youtube(cache, yt_resource)
    else:
        playlist_id = get_playlist_id_from_youtube(cache, yt_resource)

    playlist = YTPlaylist(yt_resource, playlist_id)
    playlist.fetch_videos()

    print_heading('<< VIDEOS IN THE PLAYLIST >>')
    playlist.videos().print()
    remote_serial_dict = playlist.get_videos_serial()

    print()

    renamer = Renamer(
        remote_serial_dict, files, exceptions, character_after_serial=config['character_after_serial'], padded_zero=config['padded_zero'])
    rename(renamer, cache)


@click.command()
@click.option('-c', '--character', help='Character after serial.')
@click.option('-z', '--zero', is_flag=True, help='Add zero before serial numbers to make them all of equal length.')
@click.option('-x', '--nozero', is_flag=True, help="Don't add zero before serial numbers.")
def cli(character, zero, nozero):
    if character is not None:
        config['character_after_serial'] = character

    if zero and not nozero:
        config['padded_zero'] = True
    elif not zero and nozero:
        config['padded_zero'] = False
    # else default in config is used

    if config['api_key'] is None:
        config['api_key'] = non_empty_getpass('Please provide API key: ')
        print('You can set your api key to the environment variable YOUTUBE_DATA_API_KEY, then you will not be required to input API key everytime')

    try:
        main()
    except KeyboardInterrupt:
        print('\nAborted!')
    except Exception:
        print_warning(
            'Error occured.\nPlease check your internet connection or API key.')


if __name__ == '__main__':
    # Also set this in pyproject.toml
    # [tool.poetry.scripts]
    # ytsort = "ytsort.__main__:cli"
    cli()
