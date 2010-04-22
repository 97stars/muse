import os
import re
import time

from struct import unpack

from muse.tag import flac
from muse.tag import id3


class UnsupportedFileType(Exception):
    pass


def load(filename):
    if _determine_tagtype(filename) == "FLAC":
        return _load_flac(filename)
    else:
        print "WARNING: loading tags from filename (normal for wav files)"
        return _load_filename(filename)


def save(tags, filename):
    _, extension = os.path.splitext(filename)
    for _ in xrange(5):
        # retry a few times, it seems that something in convert.py is not
        # releasing filehandles right away causing access denied errors
        try:
            if extension == ".mp3":
                _save_id3(tags, filename)
            elif extension == ".flac":
                _save_flac(tags, filename)
            else:
                raise UnsupportedFileType(
                    "saving tags to %s files is not supported" % extension)
            break
        except IOError:
            print "Warning: IOError. Retrying up to 5 times"
            time.sleep(1)


def minify(tags):
    for key in tags.keys():
        if key == "ArtistSort" and "Artist" in tags and \
                tags[key] == tags["Artist"]:
            del(tags[key])
        elif key == "AlbumArtistSort" and "AlbumArtist" in tags and \
                tags[key] == tags["AlbumArtist"]:
            del(tags[key])
        elif key == "AlbumArtist" and "Artist" in tags and \
                tags[key] == tags["Artist"]:
            del(tags[key])
    return tags


def _determine_tagtype(filename):
    with open(filename, "rb") as f:
        if unpack("3s", f.read(3))[0] == "ID3":
            return "ID3"
        f.seek(0, os.SEEK_SET)
        if unpack("4s", f.read(4))[0] == "fLaC":
            return "FLAC"
        return None


########################################
## loading
########################################


def _load_flac(filename):
    tags = {}
    for k, v in flac.load(filename):
        if k == "title":
            tags["Title"] = v
        elif k == "album":
            tags["Album"] = v
        elif k == "artist":
            tags["Artist"] = v
        elif k == "totaltracks" or k == "tracktotal":
            tags["TrackTotal"] = v
        elif k == "tracknumber":
            tags["Track"] = v
        elif k == "date":
            mdata = re.search(r"(\d\d\d\d)", v)
            tags["Year"] = mdata.group(1)
        elif k == "artistsort":
            tags["ArtistSort"] = v
        elif k == "albumartist":
            tags["AlbumArtist"] = v
        elif k == "albumartistsort":
            tags["AlbumArtistSort"] = v
    return minify(tags)


def _load_filename(filename):
    tags = {}
    (directory, fname) = os.path.split(filename)
    if directory[-1] == os.sep:
        directory = directory[:-1]
    (directory, album) = os.path.split(directory)
    if directory[-1] == os.sep:
        directory = directory[:-1]
    (_, tags["Artist"]) = os.path.split(directory)
    mdata = re.match(r"(?P<track>\d+)( - )?(?P<title>.+)\.[^.]+", fname)
    if mdata:
        tags["Title"] = mdata.group("title").strip()
        tags["Track"] = mdata.group("track").strip()
    else:
        tags["Title"] = filename.strip()
        tags["Track"] = "0"
    mdata = re.match(r"(\(\d+\)).(.+)", album)
    if mdata:
        tags["Album"] = mdata.group(2).strip()
        tags["Year"] = mdata.group(1).strip()
    else:
        tags["Album"] = album.strip()
    return tags


########################################
## saving
########################################


def _save_flac(tags, filename):
    flactags = {}
    for key in tags:
        if key == "Track":
            flactags["tracktotal"] = tags[key]
            flactags["totaltracks"] = tags[key]
        elif key == "Year":
            flactags["date"] = tags[key]
        else:
            flactags[key.lower()] = tags[key]
    flac.save(flactags, filename)


def _save_id3(tags, filename):
    frames = []
    for key in tags:
        if key == "Title":
            frames.append(id3.TIT2(tags[key]))
        elif key == "Album":
            frames.append(id3.TALB(tags[key]))
        elif key == "Artist":
            frames.append(id3.TPE1(tags[key]))
        elif key == "Track":
            if "TrackTotal" in tags:
                frames.append(
                    id3.TRCK("%s/%s" % (tags[key], tags["TrackTotal"])))
            else:
                frames.append(id3.TRCK(tags[key]))
        elif key == "Year":
            frames.append(id3.TYER(tags[key]))
        elif key == "AlbumArtist":
            frames.append(id3.TPE2(tags[key]))
        elif key == "ArtistSort":
            raise id3.ID3FrameUnsupported("ArtistSort")
        elif key == "AlbumArtistSort":
            frames.append(id3.TXXX("ALBUMARTISTSORT", tags[key]))
    id3.save(frames, filename)

########################################
## mapping data
########################################
