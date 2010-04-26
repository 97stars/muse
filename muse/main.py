import os
from fnmatch import fnmatch

from muse.convert import convert
from muse.tag.agnostic import AgnosticTags

BAD_CHARS = r"[\/:*?\"<>|]"


def start(match, target, directory, targetdir=None, copy_tags=False):
    for f in walk(directory, lambda f: fnmatch(f, match)):
        (root, _) = os.path.splitext(f)
        if targetdir:
            atags = AgnosticTags()
            atags.load(f)
            targetfile = unicode(os.path.join(targetdir,
                                              atags.name() + target))
            makepath(targetfile)
            convert(f, targetfile)
            if copy_tags:
                atags.save(targetfile)
        else:
            convert(f, root + target)


def walk(directory, wanted):
    for (root, _, files) in os.walk(directory):
        for f in files:
            if wanted(f):
                yield os.path.join(root, f)


def makepath(f):
    if not os.path.isdir(os.path.dirname(f)):
        os.makedirs(os.path.dirname(f))
