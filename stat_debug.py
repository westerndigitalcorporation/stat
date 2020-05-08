import os
import re
import sys
from cProfile import Profile
from pstats import Stats
import stat_attributes as attributes
from services import mkdir


def generateFilename(prefix=''):
    mkdir(attributes.OUTPUT_DIRECTORY, exist_ok=True)
    filename = re.sub(r'[^\w.]', '', '_{0}_{1}.csv'.format(prefix, '_'.join([arg for arg in sys.argv[1:]])))
    return '/'.join([attributes.OUTPUT_DIRECTORY, filename])

class Profiler(object):

    def __init__(self, filenamePrefix='stats'):
        self.__profiler = Profile()
        self.__filename = generateFilename(filenamePrefix)

    def enable(self, *args, **kwargs):
        self.__profiler.enable(*args, **kwargs)

    def disable(self):
        self.__profiler.disable()

    def write(self):
        with ProfileCsvStream(self.__filename, 'w') as output:
            Stats(self.__profiler, stream=output).print_stats()

    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()
        self.write()


class ProfileCsvStream(object):

    def __init__(self, *args, **kwargs):
        self.__file = open(*args, **kwargs)
        self.__row = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__close()

    def __del__(self):
        self.__close()

    def __close(self):
        if not self.__file is None:
            self.__flush()
            self.__file.flush()
            self.__file.close()
            self.__file = None

    def __flush(self):
        if self.__row:
            self.__file.write(','.join(self.__row) + '\n')
            self.__row = []

    def write(self, text):
        item = str(text).strip(' ')
        if item == '':
            return
        if item.strip():
            if item.find('ncalls') != -1:
                self.__row.extend([caption for caption in item.split()])
            else:
                self.__row.append(item)
            if item.find('\n') == -1:
                return
        self.__flush()
