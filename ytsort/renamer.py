import os

from ytsort.my_io import print_heading, print_warning


class Renamer:
    """
    Helps in renaming the files. This class contains the logic to rename the files according to the YouTube playlist.

    Attributes
    ----------
    rename_dict : dict[str, str]
        Dictionary as {<file's current name>: <file's new name>}
    serial_dict : dict[str,int]
        dictionary as {filename:serial}
    local_files : list[str]
        list containing files to be renamed
    exceptions : list[str]
        list of files not to be renamed
    __character_after_serial : str
        character to be put after serial number
    """

    def __init__(self, serial_dict: dict[str, int], local_files: list[str], exceptions: list[str], character_after_serial: str = '', padded_zero: bool = False):
        """
        Parameters
        ----------
        serial_dict: dict[str,int]
            dictionary containing key=filename and value=serial, i.e. {filename:serial}

        local_files: list[str]
            list containing files to be renamed

        exceptions: list[str]
            list of files not to be renamed

        character_after_serial: str
            character to be put after serial number

        padded_zero: bool
            If zero be prefixed or not to the serial numbers to make them all of equal lenghts
        """

        self.__character_after_serial = character_after_serial
        self.serial_dict = serial_dict
        self.local_files = local_files
        self.exceptions = exceptions
        self.rename_dict: dict[str, str] = {}
        if padded_zero:
            self._file_prefix = self.__padded_zero_file_prefix
            self._len_digits = len(str(len(serial_dict)))
            # self._len_digits=floor(log(len(serial_dict),10))+1
        else:
            self._file_prefix = self.__unpadded_zero_file_prefix

    @staticmethod
    def _remove_chars(st: str) -> str:
        """
        Remove the characters except alphanumerics.

        Parameters
        ----------
        st: str
            String in which characters are to be removed

        Returns
        -------
        : str
            New string after removing characters
        """

        st2 = ''
        for ch in st:
            if ch in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890':
                st2 += ch
        return st2

    def _file_prefix(self, serial: int) -> str:
        """
        Prefix of file to be applied. It may be only serial, or serial padded with zero.

        [Here this method is a placeholder. It will be either assigned `__padded_zero_file_prefix` or `__unpadded_zero_file_prefix` in __init__()]
        """

        # overridden in __init__()
        return ''

    def __padded_zero_file_prefix(self, serial: int) -> str:
        """
        Return serial numbers with zero prefixed to them to make them all of equal lenghts
        """

        return f'{serial:0{self._len_digits}d}'

    def __unpadded_zero_file_prefix(self, serial: int) -> str:
        """
        Return the serial number after converting to str without prefixing zero
        """

        return str(serial)

    def _update_rename_dict(self, local_filename: str, index: int):
        """Update the `rename_dict` by adding new key-value"""
        index = self._file_prefix(index)

        self.rename_dict.update(
            {local_filename: f'{index}{self.__character_after_serial} {local_filename}'})

    def generate_rename_dict(self):
        """
        Generate dictionary to be used in `start_batch_rename()` function.
        """

        for local_file in self.local_files:
            if local_file not in self.exceptions and not os.path.isdir(local_file):
                least_length_diff = 999999
                temp_remote = None
                for remote_file in self.serial_dict:
                    if self._remove_chars(remote_file) in self._remove_chars(local_file):

                        length_diff = len(local_file) - len(remote_file)
                        if length_diff < least_length_diff:
                            least_length_diff = length_diff
                            temp_remote = remote_file

                if temp_remote is None:
                    print_warning('SKIPPED:', local_file[:75]+'...')
                elif not local_file.startswith(self._file_prefix(self.serial_dict[temp_remote])):
                    self._update_rename_dict(
                        local_file, self.serial_dict[temp_remote])

        # Sorting in arranging order according to the new name i.e. value of the dictionary
        self.rename_dict = dict(
            sorted(self.rename_dict.items(), key=lambda item: item[1]))

    def is_rename_dict_formed(self) -> bool:
        return False if len(self.rename_dict) == 0 else True

    def dry_run(self):
        """Simulate the renaming process by printing the old name and new name side by side."""

        print_heading('DRY RUN')
        u = '='*19
        print(u, 'OLD', u + '\t' + u, 'NEW', u)
        for old, new in self.rename_dict.items():
            print(old[:40]+'...', end='\t')
            print(new[:40]+'...')
            print()

    def start_batch_rename(self):
        """Rename the files according to the rename_dict"""

        for old, new in self.rename_dict.items():
            try:
                os.rename(old, new)
            except Exception as e:
                print(e)
            else:
                print(f"Done: {new[:75]}...")
