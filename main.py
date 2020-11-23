from googleapiclient.discovery import build
import os

from rename_dict import RenamingHelper
from youtube_playlist import playlists_of_channel, items_of_playlist


def batch_rename(old_new: dict):
    """
    Rename the files according to the rename_dict
    :param old_new: dict{old_filename: new_filename}
    :return: void
    """
    for old, new in old_new.items():
        try:
            os.rename(old, new)
        except Exception as e:
            print(e)
        else:
            print(f"{old} renamed")


def dry_run(old_new: dict):
    print('\nDRY RUN\n')
    for old, new in old_new.items():
        print(f'OLD\t: {old}')
        print(F'NEW\t: {new}')
        print()


def main():
    api_key = os.environ.get('YOUTUBE_DATA_API_KEY')
    yt = build('youtube', 'v3', developerKey=api_key)

    from time import sleep

    avoid_file = 'avoid.txt'

    print(
        f"# If you want to ignore some files, add name of those files in {avoid_file} in the same folder in which "
        f"files to be renamed are present (or move them in another folder).\n")
    print("Input the path of the folder that contains the files to be renamed or press enter if its current folder.")
    path = input()

    if path:
        os.chdir(path)
    files = os.listdir()

    try:
        with open("channel_id.txt") as f:
            channel_id = f.read().split("\n")[0]
            print("Channel ID taken from file 'channel_id.txt' =", channel_id)
    except:
        print("Save channel ID in file 'channel_id.txt' in same folder or input below.")
        channel_id = input('Enter channel ID: ')

    avoid = [avoid_file, 'channel_id.txt', os.path.basename(__file__)]
    try:
        with open(avoid_file) as f:
            avoid.append(f.read().split("\n"))
    except:
        print("No file ignored")

    playlists = playlists_of_channel(yt, channel_id)
    # select the playlist
    select = int(input('Select from the above playlists: '))
    remote_serial_dict = items_of_playlist(yt, playlists[select])

    renaming_helper = RenamingHelper(remote_serial_dict, files, avoid)
    rename_dict = renaming_helper.get_rename_dict()

    if rename_dict:
        dry_run(rename_dict)

        confirm = input("\n\nThis can't be undone. Are you sure to rename?(y/n) : ").lower()
        print()
        if confirm == "y" or confirm == "yes":
            batch_rename(rename_dict)
        else:
            print("Nothing renamed")
    else:
        print('\nFiles already have serial number or match not found in local files and youtube videos.')
        print('Check if you have selected correct playlist.')


if __name__ == '__main__':
    main()
