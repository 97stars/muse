#!/usr/bin/env python
"""Script to fix invalid flac files created by r35 and r36 of muse"""
import os
import subprocess
import sys
from fnmatch import fnmatch
from struct import pack, unpack


def walk(directory):
    for root, dirs, files in os.walk(directory):
        for filepath in (os.path.join(root, f) for f in files):
            if fnmatch(filepath, "*.flac"):
                yield filepath


def main():
    for f in walk(unicode(sys.argv[1])):
        print f.encode("ascii", "replace")
        with open(f, "rb") as infile:
            if unpack("4s", infile.read(4))[0] == "fLaC":
                filedata, metadata = _load_file(infile)
            else:
                print "WARNING: NOT A FLAC FILE"
                continue
        with open(f, "wb") as outfile:
            outfile.write("fLaC")
            padding = None
            comments = None
            for block in metadata:
                if block['type'] == 0:
                    outfile.write(_pack_block(block))
            for block in (b for b in metadata if b['type'] != 0):
                # STREAMINFO should have been written already
                if block['type'] == 1:
                    padding = block
                elif block['type'] == 4:
                    comments = block
                elif block['type'] != 0:
                    outfile.write(_pack_block(block))
            if comments and padding:
                outfile.write(_pack_block(comments))
                outfile.write(_pack_block(padding, True))
            elif comments:
                outfile.write(_pack_block(comments, True))
            elif padding:
                outfile.write(_pack_block(padding, True))
            outfile.write(filedata)
        verify(f)


def verify(filename):
    with open(filename, "rb") as f:
        p = subprocess.Popen(["flac", "-t", "-"],
                             stdin=f,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if p.returncode != 0:
            print "ERROR: %s is still not valid" % filename.encode("ascii",
                                                                   "ignore")
            sys.exit(1)


def _pack_block(block, last=False):
    ret = ""
    header = block['type'] << 24
    header += block['length']
    if last:
        header += 1 << 31
    ret += pack(">I", header)
    ret += block['data']
    return ret


def _load_file(fh):
    blocks = []
    more_blocks = True
    while more_blocks:
        block = {}
        header = unpack(">I", fh.read(4))[0]
        if header >> 31 == 1:
            more_blocks = False
        block['type'] = (header >> 24) & 0x7f
        block['length'] = header & 0xFFFFFF
        block['data'] = fh.read(block['length'])
        blocks.append(block)
    maybe_header = unpack(">I", fh.read(4))[0]
    if maybe_header >> 31 == 0:
        # wasn't marked as the last block
        if (maybe_header >> 24) & 0x7f == 1:
            # was a padding block
            block = {}
            block['type'] = 1
            block['length'] = maybe_header & 0xFFFFFF
            block['data'] = fh.read(block['length'])
            #blocks.append(block)
    else:
        fh.seek(-4, os.SEEK_CUR)
    filedata = fh.read()
    return (filedata, blocks)


if __name__ == "__main__":
    main()
