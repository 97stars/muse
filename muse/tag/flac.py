import os
import subprocess

from struct import pack, unpack


def load(filename):
    with open(filename, "rb") as f:
        if not _is_flac(f):
            raise ValueError("%s is not a flac file" %
                             filename.encode("ascii", "replace"))
        cont = True
        while cont:
            header = unpack(">I", f.read(4))[0]
            if header >> 31 == 1:
                cont = False  # last metadata block
            length = header & 0xFFFFFF
            if (header >> 24) & 0x7F != 4:
                # not a comment block
                f.seek(length, os.SEEK_CUR)
                continue
            # ^ BIG ENDIAN
            # the FLAC format is all big endian, but vorbis comments
            # are little endian.
            # v LITTLE ENDIAN
            v_length = unpack("<I", f.read(4))[0]
            v_string = unpack("%ds" % v_length, f.read(v_length))[0]
            num_comments = unpack("<I", f.read(4))[0]
            for _ in xrange(num_comments):
                c_length = unpack("<I", f.read(4))[0]
                c_data = unpack("%ds" % c_length, f.read(c_length))[0]
                yield _parse_comment(c_data.decode("utf-8"))


def _is_flac(fh):
    return unpack("4s", fh.read(4))[0] == "fLaC"


def _parse_comment(string):
    if "=" not in string:
        raise ValueError("%s doesn't appear to be a comment" %
                         string.encode("ascii", "replace"))
    return tuple(string.split("=", 1))
