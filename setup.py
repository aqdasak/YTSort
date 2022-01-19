import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "pypiREADME.md").read_text()

# This call to setup() does all the work
setup(
    name="ytsort",
    version="1.0.1",
    description="Arrange downloaded youtube videos",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/aqdasak/YTSort/",
    author="Aqdas Ahmad Khan",
    author_email="aqdasak@gmail.com",
    packages=["ytsort"],
    include_package_data=True,
    install_requires=["click>=8.0.3, <9", "alive-progress==1.6.2",
                      "colorama>=0.3.7, <1", "google-api-python-client>=2.8.0, <3"],
    entry_points={
        "console_scripts": [
            "ytsort=ytsort.__main__:main",
        ]
    },
)
