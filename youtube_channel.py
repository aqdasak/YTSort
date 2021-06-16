from math import ceil

from progress_bar2 import ProgressBar


class YTChannel:
    def __init__(self, yt_build, channel_id) -> None:
        """
        :param yt_build: googleapiclient.discovery.build object
        :param channel_id: youtube channel ID
        """
        self._yt_build = yt_build
        self._channel_id = channel_id
        self._playlist_dict = {}
        self._selected_playlist = None
        # {Title: serial_number}
        self._videos_serial_dict = {}

    def fetch_playlists(self):
        """
        :return: dict{serial_no: playlist_id}
        """

        # List containing playlist responses by pages
        pl_response_list = []
        nextPageToken = None
        page = 1
        bar = ProgressBar()
        while True:
            pl_request = self._yt_build.playlists().list(
                part='snippet',
                channelId=self._channel_id,
                pageToken=nextPageToken
            )
            pl_response = pl_request.execute()
            pl_response_list.append(pl_response)

            if page == 1:
                bar.total = ceil(
                    pl_response['pageInfo']['totalResults'] / pl_response['pageInfo']['resultsPerPage'])
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

        self._playlist_dict = pl_dict

    def select_playlist(self, playlist_no):
        self._selected_playlist = self._playlist_dict[playlist_no]

    def generate_videos_serial(self):
        # :param playlistId: ID of the playlist
        """
        :return: dict{title: serial_no}
        """

        # List containing playlist item responses of selected playlist by pages
        pl_item_response_list = []
        nextPageToken = None
        page = 1
        bar = ProgressBar()
        while True:
            pl_item_request = self._yt_build.playlistItems().list(
                part='snippet',
                playlistId=self._selected_playlist,
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
        # {Title: serial_number}
        videos_serial_dict = {}
        i = 1
        print('<< VIDEOS IN THE PLAYLIST >>')
        for pl_item_response in pl_item_response_list:
            for item in pl_item_response['items']:
                title = item['snippet']['title']
                print(i, '-', title)
                videos_serial_dict.update({title: i})
                i += 1

        self._videos_serial_dict = videos_serial_dict

    def get_videos_serial(self):
        return self._videos_serial_dict
