import os
import subprocess

from struct import pack, unpack

class FLAC(object):

    def __init__(self, filename):
        self.file = filename

    def load(self, filename=None):
        if filename: self.file = filename
        with open(self.file, "rb") as f:
            stream_marker = unpack("4s", f.read(4))[0]
            if stream_marker != "fLaC":
                raise ValueError("%s is not a flac file" %
                                 self.file.encode("ascii", "ignore"))
            cont = True
            while(cont):
                header = unpack(">I", f.read(4))[0]
                # stop if this is the last block
                if header >> 31 == 1: cont = False
                length = header & 0xFFFFFF
                # if this isn't a comment block, we don't care
                if (header >> 24) & 0x7F != 4:
                    f.seek(length, os.SEEK_CUR)
                    continue
                # ^ BIG ENDIAN
                # flac files use big endian, but vorbis comments are all
                # little endian.. yeah..
                # v LITTLE ENDIAN
                v_length = unpack("<I", f.read(4))[0]
                v_string = unpack("%ds" % v_length, f.read(v_length))[0]
                num_comments = unpack("<I", f.read(4))[0]
                for i in xrange(num_comments):
                    c_length = unpack("<I", f.read(4))[0]
                    c_data = unpack("%ds" % c_length, f.read(c_length))[0]
                    self.__add_comment(c_data.decode("utf-8"))

    def __add_comment(self, string):
        print string.encode("ascii", "ignore")
