import os

from flac import FLAC

class AgnosticTags(object):

    def __init__(self, filename):
        self.file = filename

    def load(self, filename=None):
        if filename: self.file = filename
        (_, extension) = os.path.splitext(self.file)
        if extension == ".flac":
            self.__load_flac()

    def __load_flac(self):
        f = FLAC(self.file)
        f.load()
