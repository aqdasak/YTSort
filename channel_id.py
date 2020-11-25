import json
import os
from typing import List

from unique_list import UniqList


class UniqueChannelList(UniqList):
    def __init__(self, title=None, channel_id=None):
        self._value = []
        if title and channel_id:
            self.update(title, channel_id)
        elif (not title and channel_id) or (title and not channel_id):
            raise Exception('title and channel_id both must be passed or neither of them')

    def update(self, title, channel_id):
        super().update({'title': title, 'channel_id': channel_id})


def is_channel_id_txt_in_present(renaming_folder_path):
    path = os.getcwd()
    os.chdir(renaming_folder_path)
    files = os.listdir()
    os.chdir(path)
    if 'channel_id.txt' in files:
        return True
    return False


def is_channel_json_present(program_folder_path):
    path = os.getcwd()
    os.chdir(os.path.join(program_folder_path, 'cache'))
    files = os.listdir()
    os.chdir(path)
    if 'channel.json' in files:
        return True
    return False


def search_on_youtube(yt_build, query: str) -> list:
    pl_request = yt_build.search().list(
        part='snippet',
        type='channel',
        maxResults=9,
        q=query
    )
    pl_response = pl_request.execute()

    unique_channel_list = UniqueChannelList()
    for i, item in enumerate(pl_response['items']):
        unique_channel_list.update(title=item['snippet']['title'], channel_id=item['snippet']['channelId'])

    return unique_channel_list.list()


def print_channels(channel_with_id: List[dict]):
    for i, item in enumerate(channel_with_id):
        print(i + 1, '-', item['title'])


def add_to_channel_json(program_folder_path, channel_with_id):
    path = os.getcwd()
    os.chdir(os.path.join(program_folder_path, 'cache'))

    # unique_channel_list = UniqueChannelList()
    # if channel_id and not channel_name:
    #     channel_name = get_channel_name_from_youtube(yt_build, channel_id)
    #     unique_channel_list.update(channel_name, channel_id)
    # channel_with_id = unique_channel_list.list()

    if not is_channel_json_present(program_folder_path):
        with open('channel.json', 'w') as f:
            json.dump([channel_with_id], f, indent=4)
    elif not is_channel_id_in_channel_json(program_folder_path, channel_with_id['channel_id']):
        temp_channel_with_id = UniqueChannelList()
        with open('channel.json', 'r') as f:
            temp_channel_with_id._value = json.load(f)
            temp_channel_with_id.update(channel_with_id['title'], channel_with_id['channel_id'])
        with open('channel.json', 'w') as f:
            json.dump(temp_channel_with_id, f, indent=4)

    os.chdir(path)


def get_channel_name_from_youtube(yt_build, channel_id):
    pl_request = yt_build.channels().list(
        part='snippet',
        id=channel_id,
    )
    pl_response = pl_request.execute()
    return pl_response['items'][0]['snippet']['title']


def add_to_channel_id_txt(renaming_folder_path, channel_with_id: dict):
    path = os.getcwd()
    os.chdir(renaming_folder_path)
    with open('channel_id.txt', 'w') as f:
        json.dump(channel_with_id, f, indent=4)
    os.chdir(path)


def is_channel_id_in_channel_json(program_folder_path, channel_id):
    path = os.getcwd()
    os.chdir(os.path.join(program_folder_path, 'cache'))
    if is_channel_json_present(program_folder_path):
        with open('channel.json', 'r') as f:
            channel_with_id = json.load(f)
            for dct in channel_with_id:
                if dct['channel_id'] == channel_id:
                    return True
    os.chdir(path)
    return False


def read_from_channel_id_txt(renaming_folder_path) -> dict:
    path = os.getcwd()
    os.chdir(renaming_folder_path)
    if is_channel_id_txt_in_present(renaming_folder_path):
        with open("channel_id.txt") as f:
            channel_with_id = json.load(f)
    os.chdir(path)
    return channel_with_id


def read_from_channel_json(program_folder_path) -> list:
    path = os.getcwd()
    os.chdir(os.path.join(program_folder_path, 'cache'))
    if is_channel_json_present(program_folder_path):
        with open('channel.json', 'r') as f:
            channel_with_id = json.load(f)
    os.chdir(path)
    return channel_with_id


def get_channel_id(yt_build, program_folder_path, renaming_folder_path):
    def end(channel_with_id):
        channel_id = channel_with_id['channel_id']
        add_to_channel_json(program_folder_path, channel_with_id)
        add_to_channel_id_txt(renaming_folder_path, channel_with_id)
        return channel_id

    if is_channel_id_txt_in_present(renaming_folder_path):
        channel_with_id = read_from_channel_id_txt(renaming_folder_path)
        # if not is_channel_id_in_channel_json(program_folder_path, channel_id):
        #     channel_name = get_channel_name_from_youtube(yt_build, channel_id)
        #     channel_with_id = UniqueChannelList(channel_name, channel_id).list()
        #     # add_to_channel_json(program_folder_path, unique_channel_list.list())
        # else:
        #     channel_with_id_list = read_from_channel_json(program_folder_path)
        # # return channel_id
    else:
        if is_channel_json_present(program_folder_path):
            channel_with_id_list = read_from_channel_json(program_folder_path)
            print_channels(channel_with_id_list)
            user_input = input('Select or enter channel name to search on youtube: ')
            if user_input.isdigit():
                channel_with_id = channel_with_id_list[int(user_input) - 1]
                # channel_id = channel_with_id['channel_id']
                # add_to_channel_id_txt(renaming_folder_path, channel_id)
                # return channel_id
            else:
                channel_with_id_list = search_on_youtube(yt_build, user_input)
                print_channels(channel_with_id_list)
                user_input = int(input('Select: '))
                channel_with_id = channel_with_id_list[user_input - 1]
                # channel_id = channel_with_id['channel_id']

                # add_to_channel_json(program_folder_path, channel_with_id)
                # add_to_channel_id_txt(renaming_folder_path, channel_id)
                # return channel_id
        else:
            user_input = input('Search channel on youtube: ')
            channel_with_id_list = search_on_youtube(yt_build, user_input)
            print_channels(channel_with_id_list)
            user_input = int(input('Select: '))
            channel_with_id = channel_with_id_list[user_input - 1]
            # channel_id = channel_with_id['channel_id']

            # add_to_channel_json(program_folder_path, channel_with_id)
            # add_to_channel_id_txt(renaming_folder_path, channel_id)
            # return channel_id
    return end(channel_with_id)
