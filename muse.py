#!/usr/bin/env python
from muse.main import Muse
from muse.tag.tag import AgnosticTags

def main():
    # m = Muse("*.flac", ".mp3")
    # m.go(u"C:\\Users\\Tom\\Music\\testing\\t3")
    t = AgnosticTags(u"C:\\Users\\Tom\\Music\\testing\\t1\\08.flac")
    t.load()

if __name__ == '__main__':
    main()
