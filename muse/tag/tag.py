import os
import re

from flac import FLAC
from id3 import ID3

class UnsupportedFileType(Exception): pass

class AgnosticTags(dict):

    def __init__(self, filename):
        self.file = filename

    def load(self, filename=None):
        if filename: self.file = filename
        (_, extension) = os.path.splitext(self.file)
        if extension == ".flac":
            self.__load_flac()
        else:
            raise UnsupportedFileType("reading tags from %s files is not supported" %
                                      self.file)

    def save(self, filename=None):
        if filename: self.file = filename
        (_, extension) = os.path.splitext(self.file)
        if extension == ".mp3":
            self.__save_id3()
        else:
            raise UnsupportedFileType("saving tags to %s files is not supported" %
                                      self.file)

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

    def __save_id3(self):
        i = ID3(self.file)
        for key in self:
            if key == "Title":
                i.add_text_frame("TIT2", self[key])
            elif key == "Album":
                i.add_text_frame("TALB", self[key])
            elif key == "Artist":
                i.add_text_frame("TPE1", self[key])
            elif key == "Track":
                if "TrackTotal" in self:
                    i.add_text_frame("TRCK", "%s/%s" % (self[key], self["TrackTotal"]))
                else:
                    i.add_text_frame("TRCK", self[key])
            elif key == "Year":
                i.add_text_frame("TYER", self[key])
            elif key == "AlbumArtist":
                i.add_text_frame("TPE2", self[key])
            elif key == "ArtistSort":
                i.add_text_frame("XSOP", self[key])
            elif key == "AlbumArtistSort":
                i.add_custom_text("ALBUMARTISTSORT", self[key])
        i.save()


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
