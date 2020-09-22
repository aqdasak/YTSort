from googleapiclient.discovery import build
import os
from math import ceil

from progress_bar2 import ProgressBar

api_key = os.environ.get('YOUTUBE_DATA_API_KEY')

yt = build('youtube', 'v3', developerKey=api_key)


def playlists_of_channel(yt_build, channel_id):
    """
    :param channel_id: youtube channel ID
    :param yt_build: googleapiclient.discovery.build object
    :return: dict{serial_no: playlist_id}
    """

    # List containing playlist responses by pages
    pl_response_list = []
    nextPageToken = None
    page = 1
    bar = ProgressBar()
    while True:
        pl_request = yt_build.playlists().list(
            part='snippet',
            channelId=channel_id,
            pageToken=nextPageToken
        )
        pl_response = pl_request.execute()
        pl_response_list.append(pl_response)

        if page == 1:
            bar.total = ceil(pl_response['pageInfo']['totalResults'] / pl_response['pageInfo']['resultsPerPage'])
        bar.update(page)
        page += 1
        nextPageToken = pl_response.get('nextPageToken')
        if not nextPageToken:
            print()
            break

    # Dictionary of playlist IDs
    pl_dict = {}
    i = 1
    print('<< PLAYLISTS >>')
    for pl_response in pl_response_list:
        for item in pl_response['items']:
            print(i, '-', item['snippet']['title'])
            pl_dict.update({i: item['id']})
            i += 1

    return pl_dict


def items_of_playlist(yt_build, playlistId):
    """
    :param yt_build: googleapiclient.discovery.build object
    :param playlistId: ID of the playlist
    :return: dict{title: serial_no}
    """
    # List containing playlist item responses of selected playlist by pages
    pl_item_response_list = []
    nextPageToken = None
    page = 1
    bar = ProgressBar()
    while True:
        pl_item_request = yt_build.playlistItems().list(
            part='snippet',
            playlistId=playlistId,
            pageToken=nextPageToken
        )
        pl_item_response = pl_item_request.execute()
        pl_item_response_list.append(pl_item_response)

        if page == 1:
            bar.total = ceil(
                pl_item_response['pageInfo']['totalResults'] / pl_item_response['pageInfo']['resultsPerPage'])
        bar.update(page)
        page += 1

        nextPageToken = pl_item_response.get('nextPageToken')
        if not nextPageToken:
            print()
            break

    # Dictionary of playlist item IDs
    serial_dict = {}
    i = 1
    print('<< VIDEOS IN THE PLAYLIST >>')
    for pl_item_response in pl_item_response_list:
        for item in pl_item_response['items']:
            title = secure_filename(item['snippet']['title'])
            print(i, '-', title)
            serial_dict.update({title: i})
            i += 1
    return serial_dict


def secure_filename(file):
    """
    Replace the characters not allowed in filenames by underscore.
    :param file:
    :return:
    """
    for ch in ['/', '\\', '|', ':', '*', '?', '"', '<', '>', '+']:
        file = file.replace(ch, '_')
    return file


def dry_run(files, avoid, file_dict: dict):
    """
    Simulate the renaming of files and return to be used in batch_rename function
    :param files: list of files in the directory to be renamed
    :param avoid: list of files not to be renamed
    :param file_dict: dict{name: serial_no}
    :return: dict{old_filename: new_filename}
    """
    rename_dict = {}
    for file in files:
        if file not in avoid:
            for key in file_dict:
                if key in file and not file.startswith(str(file_dict[key])):
                    print(f'{file} -> {file_dict[key]} {file}')
                    rename_dict.update({file: f'{file_dict[key]} {file}'})
                    break
    return rename_dict


def batch_rename(rename_dict: dict):
    """
    Rename the files according to the rename_dict
    :param rename_dict: dict{old_filename: new_filename}
    :return: void
    """
    for old, new in rename_dict.items():
        try:
            os.rename(old, new)
        except Exception as e:
            print(e)
        else:
            print(f"{old} renamed")


if __name__ == '__main__':
    from time import sleep

    print(
        "# If you want to ignore some files, add name of those files in ravd.txt in the same\n"
        "# folder in which files to be renamed are present (or move them in another folder).\n")
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

    avoid = []
    try:
        with open("ravd.txt") as f:
            avoid = f.read().split("\n")
    except:
        print("No file ignored")
    avoid.append("ravd.txt")
    avoid.append(os.path.basename(__file__))

    playlists = playlists_of_channel(yt, channel_id)
    # select the playlist
    select = int(input('Select from the above playlists: '))
    video_dict = items_of_playlist(yt, playlists[select])

    print('\nDRY RUN\n')
    sleep(1)
    rename_dict = dry_run(files, avoid, video_dict)

    cnfrm = input("\n\nThis can't be undone. Are you sure to rename?(y/n) : ").lower()
    if cnfrm == "y" or cnfrm == "yes":
        batch_rename(rename_dict)
    else:
        print("Nothing renamed")
