from googleapiclient.discovery import Resource
from math import ceil

from my_io import capture_stdout, print_heading
from progress_bar2 import ProgressBar
from cache_store import CacheStore
from config import config


class Youtube:
    def __init__(self, yt_resource: Resource) -> None:
        """
        :param yt_resource: googleapiclient.discovery.build object
        """
        self._yt_resource = yt_resource
        self._channel_store = CacheStore()
        self._subscribers = []

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
        if config['show_subscribers']:
            channel_output = capture_stdout(
                lambda: self._channel_store.print())
            self._fetch_subscribers_of_all()

            print_heading('#   Channel (Subscribers)')
            for index, out in enumerate(channel_output):
                print(f'{out} ({self._subscribers[index]})')
        else:
            print_heading('#   Channel')
            self._channel_store.print()

    def select_channel(self, channel_no: int):
        return self._channel_store.list()[channel_no-1]

    def subscriber_count(self, channel_id):
        def shorten_M_K(subs: str):
            length = len(str(subs))
            subs = int(subs)
            if length > 6:
                subs /= 10**6
                subs = str(subs)
                if length >= 9:
                    subs = subs[:length-6]+'M'
                else:
                    subs = subs[:4]+'M'
            elif length > 3:
                subs /= 10**3
                subs = str(subs)
                if length == 6:
                    subs = subs[:3]+'K'
                else:
                    subs = subs[:4]+'K'
            return subs

        yt_response = self._yt_resource.channels().list(
            part='statistics',
            id=channel_id,
        ).execute()

        if yt_response['items'][0]['statistics']['hiddenSubscriberCount']:
            return

        return shorten_M_K(yt_response['items'][0]['statistics']['subscriberCount'])

    def _fetch_subscribers_of_all(self):
        def get_subs(channel_id):
            subs = self.subscriber_count(channel_id)
            if not subs:
                subs = 'Hidden'
            self._subscribers.append(subs)

        progress = ProgressBar()
        progress.total = self._channel_store.len

        for index, channel_cache_unit in enumerate(self._channel_store.list()):
            get_subs(channel_cache_unit['id'])
            progress.update(index+1)


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
        print_heading('<< PLAYLISTS >>')
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
        self._videos_store = CacheStore()

    def fetch_videos(self):
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
        print_heading('<< VIDEOS IN THE PLAYLIST >>')
        self._videos_store.print()

    def get_videos_serial(self):
        # {Title: serial_number}
        video_serial = {}
        i = 1
        for cache_unit in self._videos_store.list():
            video_serial.update({cache_unit['title']: i})
            i += 1
        return video_serial
