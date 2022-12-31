# YTSort

This program sorts the already downloaded youtube videos present in a folder by renaming them and adding serial number before their names.

# Requirements

Youtube Data API v3 is required. Get it from [here](https://console.cloud.google.com/apis/library/youtube.googleapis.com?supportedpurview=project)

# Install
###### Recommended (To install pipx click [here](https://github.com/pypa/pipx#install-pipx))
```
pipx install ytsort
```

###### or
```
pip install ytsort
```

#### Or upgrade by:
```
pipx upgrade ytsort
```
###### or
```
pip install --upgrade ytsort
```
# Usage

Set Youtube API Key to the environment variable 'YOUTUBE_DATA_API_KEY' (for ease of use, but not required).

### Execute:
```
ytsort
```

```
Usage: ytsort [OPTIONS]

Options:

  -c, --character TEXT    Character after serial.
  -z, --zero              Add zero before serial numbers to make them all of
                          equal length.
  -x, --nozero            Don't add zero before serial numbers.
  -d, --defaults          Change the default configurations and exit.
  --help                  Show this message and exit.
```

If -z & -x both are passed simultaneously then default from config.py will be used.


# Install from source
Poetry is required. For installation click [here](https://python-poetry.org/docs/#installation).

1. Download the source and install the dependencies by running:
  
   ``` 
   git clone https://github.com/aqdasak/YTSort.git
   cd YTSort
   poetry install
   ```

2. Not required but for ease of use
 
   a) Set Youtube API Key to the environment variable 'YOUTUBE_DATA_API_KEY'

   or
 
   b) edit the `config.py`:

      `'api_key': os.environ.get('YOUTUBE_DATA_API_KEY'),` to `'api_key': <Your Youtube API key>,`

### Run
In the source folder containing pyproject.toml
```
poetry shell
```

then cd into the folder containing youtube videos and execute:
```
ytsort
```
