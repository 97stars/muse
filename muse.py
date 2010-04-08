#!/usr/bin/env python
from muse.main import Muse

def main():
    m = Muse("*.flac", ".mp3")
    m.go(u"C:\\Users\\Tom\\Music\\testing\\t3")

if __name__ == '__main__':
    main()
