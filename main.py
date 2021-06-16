from googleapiclient.discovery import build
import os

from config import config
from rename_dict import RenamingHelper
# from youtube_playlist import playlists_of_channel, items_of_playlist

from channel_id import get_channel_id
# from rename_dict import batch_rename, dry_run

from youtube_channel import YTChannel


def main():
    exceptions_file = config['exceptions']

    yt_build = build('youtube', 'v3', developerKey=config['api_key'])

    print(
        f"# If you want to ignore some files, add name of those files in {exceptions_file} in the same folder in which "
        f"files to be renamed are present (or move them in another folder).\n")
    print("Input the path of the folder that contains the files to be renamed or press enter if its current folder.")
    path = input()

    if path:
        os.chdir(path)
    files = os.listdir()
    renaming_folder_path = config['renaming_folder_path']
    program_folder_path = config['program_folder_path']

    exceptions = [exceptions_file, config['local_cache'],
                  os.path.basename(__file__)]
    try:
        with open(exceptions_file) as f:
            exceptions.append(f.read().split("\n"))
    except:
        print("No file ignored\n")

    channel_id = get_channel_id(
        yt_build, program_folder_path, renaming_folder_path)

    # playlists = playlists_of_channel(yt_build, channel_id)
    # # select the playlist
    # select = int(input('Select from the above playlists: '))
    # remote_serial_dict = items_of_playlist(yt_build, playlists[select])

    channel = YTChannel(yt_build, channel_id)
    channel.fetch_playlists()
    channel.select_playlist(int(input('Select from the above playlists: ')))
    channel.generate_videos_serial()
    remote_serial_dict = channel.get_videos_serial()

    print()
    renaming_helper = RenamingHelper(
        remote_serial_dict, files, exceptions, character_after_serial=config['character_after_serial'])
    renaming_helper.generate_rename_dict()
    # rename_dict = renaming_helper.get_rename_dict()

    # if rename_dict:
    if renaming_helper.is_rename_dict_formed():
        # dry_run(rename_dict)
        renaming_helper.dry_run()

        confirm = input(
            "\n\nThis can't be undone. Are you sure to rename?(y/n) : ").lower()
        print()
        if confirm == "y" or confirm == "yes":
            # batch_rename(rename_dict)
            renaming_helper.start_batch_rename()
        else:
            print("Nothing renamed")
    else:
        print('\nFiles already have serial number or match not found in local files and youtube videos.')
        print('Check if you have selected correct playlist.')


if __name__ == '__main__':
    main()
