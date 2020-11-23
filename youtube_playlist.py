from math import ceil

from progress_bar2 import ProgressBar


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
    # {Title: serial_number}
    file_serial_number_dict = {}
    i = 1
    print('<< VIDEOS IN THE PLAYLIST >>')
    for pl_item_response in pl_item_response_list:
        for item in pl_item_response['items']:
            title = item['snippet']['title']
            print(i, '-', title)
            file_serial_number_dict.update({title: i})
            i += 1
    return file_serial_number_dict

