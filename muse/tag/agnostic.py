import os
import re
import time

from muse.tag import flac
from muse.tag import id3
from muse.utils import sanitize


class UnsupportedFileType(Exception):
    pass


class AgnosticTags(object):

    def __init__(self):
        self.tags = {}

    def add(self, desc, text):
        self.tags[desc] = text

    def name(self):
        if "AlbumArtist" in self.tags:
            artist = self.tags["AlbumArtist"]
        elif "Artist" in self.tags:
            artist = self.tags["Artist"]
        else:
            artist = "Unknown Artist"
        album = self.tags.get("Album", "Unknown Album")
        track = self.tags.get("Track", 0)
        title = self.tags.get("Title", "Unknown Title")
        return os.path.join(sanitize(artist),
                            sanitize(album),
                            sanitize("%02d %s" % (int(track), title)))

    def load(self, filename):
        tagtype = identify(filename)
        if tagtype == "FLAC":
            self.load_flac(filename)
        else:
            self.load_filename(filename)

    def save(self, filename):
        _, extension = os.path.splitext(filename)
        for _ in xrange(5):
            # retry a few times, it seems that something in convert.py is not
            # releasing filehandles right away causing access denied errors
            try:
                if extension == ".mp3":
                    self.save_id3(filename)
                elif extension == ".flac":
                    self.save_flac(filename)
                else:
                    raise UnsupportedFileType(
                        "saving tags to %s files is not supported" % extension)
                break
            except IOError:
                print "Warning: IOError. Retrying up to 5 times"
                time.sleep(1)

    def load_flac(self, filename):
        flactags = flac.FLAC()
        for k, v in flactags.load(filename):
            if k == "title":
                self.tags["Title"] = v
            elif k == "album":
                self.tags["Album"] = v
            elif k == "artist":
                self.tags["Artist"] = v
            elif k == "totaltracks" or k == "tracktotal":
                self.tags["TrackTotal"] = v
            elif k == "tracknumber":
                self.tags["Track"] = v
            elif k == "date":
                mdata = re.search(r"(\d\d\d\d)", v)
                self.tags["Year"] = mdata.group(1)
            elif k == "artistsort":
                self.tags["ArtistSort"] = v
            elif k == "albumartist":
                self.tags["AlbumArtist"] = v
            elif k == "albumartistsort":
                self.tags["AlbumArtistSort"] = v
        self.minify()

    def load_id3(self, filename):
        pass

    def load_filename(self, filename):
        (directory, fname) = os.path.split(filename)
        if directory[-1] == os.sep:
            directory = directory[:-1]
        (directory, album) = os.path.split(directory)
        if directory[-1] == os.sep:
            directory = directory[:-1]
        (_, self.tags["Artist"]) = os.path.split(directory)
        mdata = re.match(r"(?P<track>\d+)( - )?(?P<title>.+)\.[^.]+", fname)
        if mdata:
            self.tags["Title"] = mdata.group("title").strip()
            self.tags["Track"] = mdata.group("track").strip()
        else:
            self.tags["Title"] = filename.strip()
            self.tags["Track"] = "0"
        mdata = re.match(r"(\(\d+\)).(.+)", album)
        if mdata:
            self.tags["Album"] = mdata.group(2).strip()
            self.tags["Year"] = mdata.group(1).strip()
        else:
            self.tags["Album"] = album.strip()

    def save_flac(self, filename):
        flactags = flac.FLAC()
        for key in self.tags:
            if key == "Track":
                flactags.add("tracktotal", self.tags[key])
                flactags.add("totaltracks", self.tags[key])
            elif key == "Year":
                flactags.add("date", self.tags[key])
            else:
                flactags.add(key.lower(), self.tags[key])
        flactags.save(filename)

    def save_id3(self, filename):
        id3tags = id3.ID3()
        for key in self.tags:
            if key == "Title":
                id3tags.add(id3.TIT2(self.tags[key]))
            elif key == "Album":
                id3tags.add(id3.TALB(self.tags[key]))
            elif key == "Artist":
                id3tags.add(id3.TPE1(self.tags[key]))
            elif key == "Track":
                if "TrackTotal" in self.tags:
                    id3tags.add(
                        id3.TRCK(
                            "%s/%s" %
                            (self.tags[key], self.tags["TrackTotal"])))
                else:
                    id3tags.add(id3.TRCK(self.tags[key]))
            elif key == "Year":
                id3tags.add(id3.TYER(self.tags[key]))
            elif key == "AlbumArtist":
                id3tags.add(id3.TPE2(self.tags[key]))
                id3tags.add(id3.TXXX("ALBUM ARTIST", self.tags[key]))
            elif key == "ArtistSort":
                id3tags.add(id3.XSOP(self.tags[key]))
            elif key == "AlbumArtistSort":
                id3tags.add(id3.TXXX("ALBUMARTISTSORT", self.tags[key]))
        id3tags.save(filename)

    def minify(self):
        for key in self.tags.keys():
            if key == "ArtistSort" and "Artist" in self.tags and \
                    self.tags[key] == self.tags["Artist"]:
                del(self.tags[key])
            elif key == "AlbumArtistSort" and "AlbumArtist" in self.tags and \
                self.tags[key] == self.tags["AlbumArtist"]:
                del(self.tags[key])
            elif key == "AlbumArtist" and "Artist" in self.tags and \
                    self.tags[key] == self.tags["Artist"]:
                del(self.tags[key])


def identify(filename):
    with open(filename, "rb") as f:
        if flac.identify(f):
            return "FLAC"
        elif id3.identify(f):
            return "ID3"


########################################
## mapping data
########################################
