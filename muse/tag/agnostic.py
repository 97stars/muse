import os
import re
import time

import flac
import id3

class UnsupportedFileType(Exception): pass

def load(filename):
    _, extension = os.path.splitext(filename)
    if extension == ".flac":
        return _load_flac(filename)
    else:
        raise UnsupportedFileType("reading tags from %s files is not supported" %
                                  extension)

def save(tags, filename):
    _, extension = os.path.splitext(filename)
    for _ in xrange(5):
        # retry a few times, it seems that something in convert.py is not
        # releasing filehandles right away causing access denied errors
        try:
            if extension == ".mp3":
                _save_id3(tags, filename)
            else:
                raise UnsupportedFileType("saving tags to %s files is not supported" %
                                          extension)
            break
        except IOError:
            print "Warning: IOError. Retrying up to 5 times"
            time.sleep(1)

def minify(tags):
    pass

########################################
## loading
########################################

def _load_flac(filename):
    with open(filename, "rb") as f:
        pass

########################################
## saving
########################################

def _save_id3(filename):
    pass

########################################
## mapping data
########################################


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
        for k, v in flac.load(self.file):
            if k == "title":
                self["Title"] = v
            elif k == "album":
                self["Album"] = v
            elif k == "artist":
                self["Artist"] = v
            elif k == "totaltracks" or k == "tracktotal":
                self["TrackTotal"] = v
            elif k == "tracknumber":
                self["Track"] = v
            elif k == "date":
                mdata = re.search(r"(\d\d\d\d)", v)
                self["Year"] = mdata.group(1)
            elif k == "artistsort":
                self["ArtistSort"] = v
            elif k == "albumartist":
                self["AlbumArtist"] = v
            elif k == "albumartistsort":
                self["AlbumArtistSort"] = v
        self.minify()
