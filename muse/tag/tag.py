import os
import re

from flac import FLAC

class AgnosticTags(dict):

    def __init__(self, filename):
        self.file = filename

    def load(self, filename=None):
        if filename: self.file = filename
        (_, extension) = os.path.splitext(self.file)
        if extension == ".flac":
            self.__load_flac()

    def minify(self):
        for key in self.keys():
            if key == "ArtistSort" and "Artist" in self and \
                    self[key] == self["Artist"]:
                del(self[key])
            elif key == "AlbumArtistSort" and "AlbumArtist" in self and \
                    self[key] == self["AlbumArtist"]:
                del(self[key])
            elif key == "AlbumArtist" and "Artist" in self and \
                    self[key] == self["Artist"]:
                del(self[key])

    def __load_flac(self):
        f = FLAC(self.file)
        f.load()
        for k in f:
            if k == "title":
                self["Title"] = f[k]
            elif k == "album":
                self["Album"] = f[k]
            elif k == "artist":
                self["Artist"] = f[k]
            elif k == "totaltracks" or k == "tracktotal":
                self["TrackTotal"] = f[k]
            elif k == "tracknumber":
                self["Track"] = f[k]
            elif k == "date":
                mdata = re.search(r"(\d\d\d\d)", f[k])
                self["Year"] = mdata.group(1)
            elif k == "artistsort":
                self["ArtistSort"] = f[k]
            elif k == "albumartist":
                self["AlbumArtist"] = f[k]
            elif k == "albumartistsort":
                self["AlbumArtistSort"] = f[k]
        self.minify()
