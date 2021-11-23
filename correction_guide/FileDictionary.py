import os
import re


class FileDictionary:
    """Data structure that represents a dictionary at runtime as well as when the program is not running"""

    def __init__(self, file_path: str):
        """Initializes the FileDictionary with a specified file_path"""
        if os.path.exists(file_path) and file_path.endswith('.dict'):
            self.file_path = file_path
            print('INFO: file at ' + file_path + ' was mounted successfully')
        else:
            print('ERROR: file path does not exist')
            exit(1)
        self.dictionary: dict = {}
        self.__parse_file()

    def __parse_file(self):
        """Parses the dictionary contents of the file in the format 'key :: value' and saves them to self.dict"""
        with open(self.file_path, mode='r', errors='strict') as f:
            for entry in f.readlines():
                if str(entry).strip() != '':
                    # check if line matches the FileDictionary structure
                    if re.match(r'^[a-zA-Z0-9.]+ :: .+$', str(entry)):
                        # get key and value and save them to self.dict
                        key, value = entry.split(' :: ', 1)
                        self.dictionary[key] = value
                    else:
                        print('ERROR: line cannot be parsed:\n' + str(entry).strip())

    def __write_file(self):
        """Synchronizes the dictionary with the file by writing its contents to it"""
        file_representation = []
        for key, value in self.dictionary.items():
            # creating a string representation of the dictionary
            file_representation.append(f'{key} :: {value}\n')
        with open(self.file_path, mode='w', errors='strict') as f:
            f.writelines(file_representation)

    def get(self, key):
        """Simple getter method to retrieve the value"""
        try:
            return self.dictionary[key]
        except KeyError:
            print('INFO: key was not found in the dictionary')

    def insert(self, key: str, value: str, prefix: str = ''):
        """Inserts a key,value pair into the dictionary, if no key is specified one is created from the prefix"""
        if key == '':
            # if key is empty, a key is created by using the specified prefix and a unique number
            key = str(len(self.dictionary))
        key = prefix + key
        self.dictionary[key] = value
        # dictionary is sorted
        self.dictionary = dict(sorted(self.dictionary.items()))
        # syncing with the file
        self.__write_file()

    def delete(self, key):
        """Deletes a key,value pair from the dictionary, then syncs it with the file"""
        value = self.dictionary[key]
        del self.dictionary[key]
        self.__write_file()
        return value
