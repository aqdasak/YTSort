from typing import List
from distinct_channel import DistinctChannel


def search_channel_on_youtube(yt_build, query: str) -> list:
    pl_request = yt_build.search().list(
        part='snippet',
        type='channel',
        maxResults=9,
        q=query
    )
    pl_response = pl_request.execute()

    unique_channel_list = DistinctChannel()
    for _, item in enumerate(pl_response['items']):
        unique_channel_list.update(
            title=item['snippet']['title'], channel_id=item['snippet']['channelId']
        )

    return unique_channel_list.list()


def print_channels(channel_with_id: List[dict]):
    for i, item in enumerate(channel_with_id):
        print(i + 1, '-', item['title'])
