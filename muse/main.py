import os
from fnmatch import fnmatch

from convert import convert

class Muse:

    def __init__(self, match, target):
        self.match = match
        self.target = target

    def go(self, directory):
        for f in self.walk(directory, lambda f: fnmatch(f, self.match)):
            (root, _) = os.path.splitext(f)
            newfile = convert(f, root + self.target)

    def walk(self, directory, wanted):
        for (root, dirs, files) in os.walk(directory):
            for f in files:
                if wanted(f): yield os.path.join(root, f)
