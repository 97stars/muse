import os
from struct import pack, unpack

class ID3Error(Exception): pass

class ID3(dict):

    def __init__(self, filename=None):
        self.file = filename
        self.__version = (3, 0)

    def save(self, filename=None):
        if filename: self.file = filename
        if os.path.exists(self.file):
            with open(self.file, "rb") as f:
                filedata = _load_file(f)
        else: filedata = "" # filedata is blank if we're saving to a new file
        framedata = self.__pack_frames();
        with open(self.file, "wb") as f:
            f.write(pack(">3s BB B",
                         "ID3",
                         self.__version[0], self.__version[1],
                         0))
            f.write(_pack_id3_size(len(framedata)))
            f.write(framedata)
            f.write(filedata)

    def add_text_frame(self, ident, text):
        self[ident] = unicode(text)

    def add_custom_text(self, desc, text):
        self["TXXX"] = {"DESC": desc, "TEXT": text}

    def __pack_frames(self):
        framedata = ""
        for frame_id in self:
            if frame_id == "TXXX":
                desc = self[frame_id]["DESC"].encode("UTF-16")
                text = self[frame_id]["TEXT"].encode("UTF-16")
                frametext = pack(">B", 1) # encoding
                frametext += pack(">%dsxx%ds" % (len(desc), len(text)),
                                  desc, text)
            else:
                if frame_id == "TYER":
                    text = self[frame_id].encode("iso-8859-1")
                    frametext = pack(">B", 0)
                elif frame_id == "TRCK":
                    text = self[frame_id].encode("iso-8859-1")
                    frametext = pack(">B", 0)
                else:
                    text = self[frame_id].encode("UTF-16")
                    frametext = pack(">B", 1) # encoding
                frametext += pack(">%ds" % len(text), text)
            # start of header
            framedata += pack(">4s", frame_id)
            framedata += pack(">I", len(frametext))
            framedata += pack(">H", 0)
            # end of header
            framedata += frametext
        return framedata

def _is_id3(fh):
    fh.seek(0, os.SEEK_SET)
    ident = unpack(">3s", fh.read(3))[0]
    fh.seek(0, os.SEEK_SET)
    return ident == "ID3"

def _load_file(fh):
    fh.seek(0, os.SEEK_SET)
    if _is_id3(fh):
        fh.seek(6, os.SEEK_SET)
        packedsize = unpack("BBBB", fh.read(4))
        size = _unpack_id3_size(packedsize)
        fh.seek(size + 10, os.SEEK_SET)
    return fh.read()

def _pack_id3_size(size):
    ret = []
    ret.append(size & 0x7F)
    for _ in xrange(3):
        size >>= 7
        ret.append(size & 0x7F)
    ret.reverse()
    return pack(">BBBB", *ret)

def _unpack_id3_size(packedsize):
    ret = packedsize[0]
    for i in xrange(1, 4):
        ret <<= 7
        ret += packedsize[i]
    return ret
