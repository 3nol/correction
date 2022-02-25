import os
import re


class FileDictionary:
    """Data structure that represents a dictionary at runtime as well as when the program is not running"""

    def __init__(self, file_path: str):
        """Initializes the FileDictionary with a specified file_path"""
        if os.path.exists(file_path) and file_path.endswith('.dict'):
            self.file_path = file_path
            print('INFO: file at \'' + file_path + '\' was mounted successfully')
        else:
            print('ERROR: file path \'' + file_path + '\' does not exist')
            exit(1)
        self.__dictionary: dict = {}
        self.__parse_file()

    def __parse_file(self):
        """Parses the dictionary contents of the file in the format 'key :: value' and saves them to self.dict"""
        with open(self.file_path, mode='r', errors='strict', encoding='utf-8') as f:
            for entry in f.readlines():
                if str(entry).strip() != '':
                    # check if line matches the FileDictionary structure
                    if re.match(r'^[^:]+ :: .+$', str(entry)):
                        # get key and value and save them to self.dict
                        key, value = str(entry).split(' :: ', 1)
                        self.__dictionary[key] = str(value).strip()
                    else:
                        print('ERROR: line cannot be parsed:\n' + str(entry).strip())

    def __write_file(self):
        """Synchronizes the dictionary with the file by writing its contents to it"""
        file_representation = []
        for key, value in self.__dictionary.items():
            # creating a string representation of the dictionary
            file_representation.append(f'{key} :: {value}\n')
        with open(self.file_path, mode='w', errors='strict', encoding='utf-8') as f:
            f.writelines(file_representation)

    def get(self, key, errors=False):
        """Simple getter method to retrieve the value"""
        try:
            return self.__dictionary[key]
        except KeyError:
            if errors:
                print('ERROR: key was not found in the dictionary')

    def insert(self, key: str, value: str, prefix: str = '', errors=False):
        """Inserts a key,value pair into the dictionary, if no key is specified one is created from the prefix"""
        if key == '':
            # if key is empty, a key is created by using the specified prefix and a unique number
            key = str(len(self.__dictionary))
        key = prefix + key
        if errors and self.get(key, errors=False) is not None:
            print('INFO: overwriting value for key: ' + key)
        self.__dictionary[key] = value
        # dictionary is sorted
        self.__dictionary = dict(sorted(self.__dictionary.items()))
        # syncing with the file
        self.__write_file()

    def delete(self, key, errors=False):
        """Deletes a key,value pair from the dictionary, then syncs it with the file"""
        value = self.get(key, errors)
        if value is not None:
            del self.__dictionary[key]
            self.__write_file()
            return value
