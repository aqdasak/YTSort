# YTSort

This program sorts the already downloaded youtube videos present in a folder by renaming them and adding serial number before their names.

# Requirements

Youtube Data API v3 is required. Get it from [here](https://console.cloud.google.com/apis/library/youtube.googleapis.com?supportedpurview=project)


# Usage

Set Youtube API Key to the environment variable 'YOUTUBE_DATA_API_KEY' (for ease of use, but not required).

### Execute:
```
ytsort
```
ytsort [Options]

Options:

    -c, --character TEXT   Character after serial.

    -p, --padded-zero      Padded zero.

    -np, --no-padded-zero  No padded zero.

    --help                 Show help.

If -p & -np both are passed simultaneously then default from config.py will be used.

