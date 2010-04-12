import os
import re
import time

import id3
from flac import FLAC

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
        for _ in xrange(5):
            # sometimes shit just doesn't work, so lets try a few times...
            try:
                if extension == ".mp3":
                    self.__save_id3()
                else:
                    raise UnsupportedFileType("saving tags to %s files is not supported" %
                                              self.file)
                break
            except IOError:
                print "Warning: IOError occured"
                time.sleep(1)

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
        frames = []
        for key in self:
            if key == "Title":
                frames.append(id3.TIT2(self[key]))
            elif key == "Album":
                frames.append(id3.TALB(self[key]))
            elif key == "Artist":
                frames.append(id3.TPE1(self[key]))
            elif key == "Track":
                if "TrackTotal" in self:
                    frames.append(id3.TRCK("%s/%s" % (self[key], self["TrackTotal"])))
                else:
                    frames.append(id3.TRCK(self[key]))
            elif key == "Year":
                frames.append(id3.TYER(self[key]))
            elif key == "AlbumArtist":
                frames.append(id3.TPE2(self[key]))
            elif key == "ArtistSort":
                raise id3.ID3FrameUnsupported("ArtistSort")
            elif key == "AlbumArtistSort":
                frames.append(id3.TXXX("ALBUMARTISTSORT", self[key]))
        id3.save(frames, self.file)


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
