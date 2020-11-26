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


def add_to_channel_id_txt(renaming_folder_path, channel_with_id: dict):
    path = os.getcwd()
    os.chdir(renaming_folder_path)
    with open('channel_id.txt', 'w') as f:
        json.dump(channel_with_id, f, indent=4)
    os.chdir(path)


def read_from_channel_id_txt(renaming_folder_path) -> dict:
    path = os.getcwd()
    os.chdir(renaming_folder_path)
    with open("channel_id.txt") as f:
        channel_with_id = json.load(f)
    os.chdir(path)
    return channel_with_id


def add_to_channel_json(program_folder_path, channel_with_id):
    def is_channel_id_in_channel_json(program_folder_path, channel_id):
        path = os.getcwd()
        os.chdir(os.path.join(program_folder_path, 'cache'))
        with open('channel.json', 'r') as f:
            channel_with_id = json.load(f)
            for dct in channel_with_id:
                if dct['channel_id'] == channel_id:
                    return True
        os.chdir(path)
        return False

    path = os.getcwd()
    os.chdir(os.path.join(program_folder_path, 'cache'))

    if not is_channel_json_integrated(program_folder_path):
        with open('channel.json', 'w') as f:
            json.dump([channel_with_id], f, indent=4)
    elif not is_channel_id_in_channel_json(program_folder_path, channel_with_id['channel_id']):
        temp_channel_with_id = UniqueChannelList()
        with open('channel.json', 'r') as f:
            temp_channel_with_id._value = json.load(f)
            temp_channel_with_id.update(channel_with_id['title'], channel_with_id['channel_id'])
        with open('channel.json', 'w') as f:
            json.dump(temp_channel_with_id.list(), f, indent=4)

    os.chdir(path)


def read_from_channel_json(program_folder_path) -> list:
    path = os.getcwd()
    os.chdir(os.path.join(program_folder_path, 'cache'))
    with open('channel.json', 'r') as f:
        channel_with_id = json.load(f)
    os.chdir(path)
    return channel_with_id


def check_integrity(path, filename) -> bool:
    def check(channel_with_id) -> bool:
        if type(channel_with_id) == dict:
            title, channel_id = channel_with_id.keys()
            if title != 'title' or channel_id != 'channel_id':
                return False
        elif type(channel_with_id) == list:
            for item in channel_with_id:
                r = check(item)
                if r is False:
                    return r
            else:
                return True
        else:
            return False

    try:
        with open(os.path.join(path, filename)) as f:
            try:
                channel_with_id = json.load(f)
                return_value = check(channel_with_id)
                return True if return_value is None else return_value
            except:
                return False
    except:
        return False


def is_channel_id_txt_integrated(renaming_folder_path):
    return check_integrity(renaming_folder_path, 'channel_id.txt')


def is_channel_json_integrated(program_folder_path):
    return check_integrity(os.path.join(program_folder_path, 'cache'), 'channel.json')


def get_channel_id(yt_build, program_folder_path, renaming_folder_path):
    def end(channel_with_id):
        channel_id = channel_with_id['channel_id']
        add_to_channel_json(program_folder_path, channel_with_id)
        add_to_channel_id_txt(renaming_folder_path, channel_with_id)
        return channel_id

    if is_channel_id_txt_integrated(renaming_folder_path):
        channel_with_id = read_from_channel_id_txt(renaming_folder_path)
    else:
        if is_channel_json_integrated(program_folder_path):
            channel_with_id_list = read_from_channel_json(program_folder_path)
            print_channels(channel_with_id_list)
            user_input = input('Select or enter channel name to search on youtube: ')
            if user_input.isdigit():
                channel_with_id = channel_with_id_list[int(user_input) - 1]
            else:
                channel_with_id_list = search_on_youtube(yt_build, user_input)
                print_channels(channel_with_id_list)
                user_input = int(input('Select: '))
                channel_with_id = channel_with_id_list[user_input - 1]
        else:
            user_input = input('Search channel on youtube: ')
            channel_with_id_list = search_on_youtube(yt_build, user_input)
            print_channels(channel_with_id_list)
            user_input = int(input('Select: '))
            channel_with_id = channel_with_id_list[user_input - 1]

    return end(channel_with_id)
