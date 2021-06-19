from my_io import print_heading, print_warning
import os
from typing import List


class RenamingHelper:
    def __init__(self, serial_dict: dict, local_files: List[str], exceptions: List[str], character_after_serial=')'):
        """
        :param serial_dict:
        :param local_files:
        :param exceptions: list of files not to be renamed
        """
        self.__character_after_serial = character_after_serial
        self.serial_dict = serial_dict
        self.local_files = local_files
        self.exceptions = exceptions
        self.rename_dict = {}

    @staticmethod
    def _remove_chars(st: str):
        """
        Remove the characters except alphanumerics.
        :param st: String in which characters are to be removed
        :return: New string after removing characters
        """
        st2 = ''
        for ch in st:
            if ch in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890':
                st2 += ch
        return st2

    def _update_rename_dict(self, local_filename: str, index: int):
        self.rename_dict.update(
            {local_filename: f'{index}{self.__character_after_serial} {local_filename}'})

    def generate_rename_dict(self):
        """
        Simulate the renaming of files and generate dictionary to be used in batch_rename function
        """

        for local_file in self.local_files:
            if local_file not in self.exceptions and not os.path.isdir(local_file):
                least_length_diff = 1000
                temp_remote = None
                for remote_file in self.serial_dict:
                    if self._remove_chars(remote_file) in self._remove_chars(local_file):

                        length_diff = len(local_file) - len(remote_file)
                        if (length_diff) < least_length_diff:
                            least_length_diff = length_diff
                            temp_remote = remote_file

                if temp_remote is None:
                    print_warning('SKIPPED:', local_file[:75]+'...')
                elif not local_file.startswith(str(self.serial_dict[temp_remote])):
                    self._update_rename_dict(
                        local_file, self.serial_dict[temp_remote])

    def is_rename_dict_formed(self) -> bool:
        return False if len(self.rename_dict) == 0 else True

    def dry_run(self):
        print_heading('DRY RUN')
        u = '='*19
        print(u, 'OLD', u + '\t' + u, 'NEW', u)
        for old, new in self.rename_dict.items():
            print(old[:40]+'...', end='\t')
            print(new[:40]+'...')
            print()

    def start_batch_rename(self):
        """
        Rename the files according to the rename_dict   
        :return: void
        """
        for old, new in self.rename_dict.items():
            try:
                os.rename(old, new)
            except Exception as e:
                print(e)
            else:
                print(f"Done: {new[:75]}...")
