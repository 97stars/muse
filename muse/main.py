import os
import re
from fnmatch import fnmatch

from muse.convert import convert
from muse.tag import agnostic

BAD_CHARS = r"[\/:*?\"<>|]"


class Muse:

    def __init__(self, match, target):
        self.match = match
        self.target = target

    def go(self, directory, targetdir=None, copy_tags=False):
        for f in self.walk(directory, lambda f: fnmatch(f, self.match)):
            (root, _) = os.path.splitext(f)
            if targetdir:
                tags = agnostic.load(f)
                if "AlbumArtist" in tags:
                    artist = tags["AlbumArtist"]
                else:
                    artist = tags["Artist"]
                targetfile = unicode(
                    os.path.join(targetdir,
                                 _sanitize(artist),
                                 _sanitize(tags["Album"]),
                                 _sanitize("%02d %s" % (int(tags["Track"]),
                                                        tags["Title"]) +
                                           self.target)))
                _makepath(targetfile)
                convert(f, targetfile)
                if copy_tags:
                    agnostic.save(tags, targetfile)
            else:
                convert(f, root + self.target)

    def walk(self, directory, wanted):
        for (root, _, files) in os.walk(directory):
            for f in files:
                if wanted(f):
                    yield os.path.join(root, f)


def _makepath(f):
    if not os.path.isdir(os.path.dirname(f)):
        os.makedirs(os.path.dirname(f))


def _sanitize(f):
    s = re.sub("\.$", "_", f)
    s = re.sub("^\.", "_", s)
    return re.sub(BAD_CHARS, "_", s)
