from googleapiclient.discovery import Resource
from math import ceil

from my_io import print_heading
from progress_bar2 import ProgressBar
from cache_store import CacheStore


class Youtube:
    def __init__(self, yt_resource: Resource) -> None:
        """
        :param yt_resource: googleapiclient.discovery.build object
        """
        self._yt_resource = yt_resource
        self._channel_store = CacheStore()

    def search_channel(self, query: str) -> list:
        yt_request = self._yt_resource.search().list(
            part='snippet',
            type='channel',
            maxResults=9,
            q=query
        )
        yt_response = yt_request.execute()

        for item in yt_response['items']:
            self._channel_store.update(
                title=item['snippet']['title'], id=item['snippet']['channelId']
            )

    def print_channels(self):
        self._channel_store.print()

    def select_channel(self, channel_no: int):
        return self._channel_store.list()[channel_no-1]


class YTChannel:
    def __init__(self, yt_resource: Resource, channel_id) -> None:
        """
        :param yt_resource: googleapiclient.discovery.Resource object
        :param channel_id: youtube channel ID
        """
        self._yt_resource = yt_resource
        self._channel_id = channel_id
        self._playlist_store = CacheStore()

    def fetch_playlists(self):
        """
        :return: dict{serial_no: playlist_id}
        """

        # List containing playlist responses by pages
        # pl_response_list = []
        nextPageToken = None
        page = 1
        bar = ProgressBar()
        while True:
            pl_request = self._yt_resource.playlists().list(
                part='snippet',
                channelId=self._channel_id,
                pageToken=nextPageToken
            )
            pl_response = pl_request.execute()
            # pl_response_list.append(pl_response)

            for item in pl_response['items']:
                self._playlist_store.update(
                    title=item['snippet']['title'], id=item['id']
                )

            if page == 1:
                bar.total = ceil(
                    pl_response['pageInfo']['totalResults'] / pl_response['pageInfo']['resultsPerPage'])
            bar.update(page)
            page += 1
            nextPageToken = pl_response.get('nextPageToken')
            if not nextPageToken:
                print()
                break

    def print_playlists(self):
        print_heading('PLAYLISTS')
        self._playlist_store.print()

    def select_playlist(self, playlist_no):
        return self._playlist_store.list()[playlist_no-1]


class YTPlaylist:
    def __init__(self, yt_resource: Resource, playlist_id) -> None:
        """
        :param yt_resource: googleapiclient.discovery.Resource object
        :param playlist_id: youtube playlist ID
        """
        self._yt_resource = yt_resource
        self._playlist_id = playlist_id
        # {Title: serial_number}
        # self._videos_serial_dict = {}
        self._videos_store = CacheStore()

    def fetch_videos(self):
        """
        :return: dict{title: serial_no}
        """

        # List containing playlist item responses of selected playlist by pages
        # pl_item_response_list = []
        nextPageToken = None
        page = 1
        bar = ProgressBar()
        while True:
            pl_item_request = self._yt_resource.playlistItems().list(
                part='snippet',
                playlistId=self._playlist_id,
                pageToken=nextPageToken
            )
            pl_item_response = pl_item_request.execute()
            # pl_item_response_list.append(pl_item_response)

            for item in pl_item_response['items']:
                self._videos_store.update(
                    title=item['snippet']['title'], id='#'
                )

            if page == 1:
                bar.total = ceil(
                    pl_item_response['pageInfo']['totalResults'] / pl_item_response['pageInfo']['resultsPerPage'])
            bar.update(page)
            page += 1

            nextPageToken = pl_item_response.get('nextPageToken')
            if not nextPageToken:
                print()
                break

    def print_videos(self):
        print_heading('VIDEOS IN THE PLAYLIST')
        self._videos_store.print()

    def get_videos_serial(self):
        video_serial = {}
        i = 1
        for cache_unit in self._videos_store.list():
            video_serial.update({cache_unit['title']: i})
            i += 1
        return video_serial
