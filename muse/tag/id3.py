import os
from struct import pack, unpack

VERSION = (3, 0)  # ID3v2 version


class Error(Exception):
    pass


class ID3(object):

    def __init__(self):
        self.frames = []

    def add(self, tag):
        self.frames.append(tag)

    def load(self, filename):
        pass

    def save(self, filename):
        filedata = _load_file(filename)
        framedata = "".join([x.pack() for x in self.frames])
        header = _id3_header(len(framedata))
        with open(filename, "wb") as f:
            f.write(header)
            f.write(framedata)
            f.write(filedata)


def identify(fh):
    fh.seek(0, os.SEEK_SET)
    return "ID3" == unpack(">3s", fh.read(3))[0]


def _load_file(filename):
    if not os.path.exists(filename):
        return ""
    with open(filename, "rb") as f:
        seek = 0
        if identify(f):
            f.seek(6, os.SEEK_SET)
            seek = _unpack_id3_size(unpack(">BBBB", f.read(4)))
        f.seek(seek, os.SEEK_SET)
        return f.read()


def _id3_header(size):
    header = pack(">3s BB B", "ID3", VERSION[0], VERSION[1], 0)
    header += _pack_id3_size(size)
    return header


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


###############################################################################
## ID3 Frame Classes
###############################################################################


class ID3Frame(object):

    id = "NONE"

    def __init__(self):
        self.flags = 0

    def pack(self):
        length = len(self.packed_data)
        return pack(">4s", self.id) + pack(">I", length) + \
            pack(">H", self.flags) + self.packed_data


class ID3TextFrame(ID3Frame):

    encodings = {
        0: "iso-8859-1",
        1: "utf-16",
        }

    def __init__(self, text):
        ID3Frame.__init__(self)
        self.text = text
        self.encoding = 1
        self.__packed_text = None

    def __packed_text(self):
        if not self.__packed_text:
            etext = self.text.encode(self.encodings[self.encoding])
            length = len(etext)
            self.__packed_text = pack(">B%ds" % length, self.encoding, etext)
        return self.__packed_text

    packed_data = property(__packed_text)
    packed_text = property(__packed_text)


class ID3NumericTextFrame(ID3TextFrame):

    def __init__(self, text):
        ID3TextFrame.__init__(self, text)
        self.encoding = 0

class AENC(): pass
class APIC(): pass
class COMM(): pass
class COMR(): pass
class ENCR(): pass
class EQUA(): pass
class ETCO(): pass
class GEOB(): pass
class GRID(): pass
class IPLS(): pass
class LINK(): pass
class MCDI(): pass
class MLLT(): pass
class OWNE(): pass
class PRIV(): pass
class PCNT(): pass
class POPM(): pass
class POSS(): pass
class RBUF(): pass
class RVAD(): pass
class RVRB(): pass
class SYLT(): pass
class SYTC(): pass
class TALB(ID3TextFrame): id = "TALB"
class TBPM(): pass
class TCOM(): pass
class TCON(): pass
class TCOP(): pass
class TDAT(): pass
class TDLY(): pass
class TENC(): pass
class TEXT(): pass
class TFLT(): pass
class TIME(): pass
class TIT1(ID3TextFrame): id = "TIT1"
class TIT2(ID3TextFrame): id = "TIT2"
class TIT3(ID3TextFrame): id = "TIT3"
class TKEY(): pass
class TLAN(): pass
class TLEN(): pass
class TMED(): pass
class TOAL(): pass
class TOFN(): pass
class TOLY(): pass
class TOPE(): pass
class TORY(): pass
class TOWN(): pass
class TPE1(ID3TextFrame): id = "TPE1"
class TPE2(ID3TextFrame): id = "TPE2"
class TPE3(): pass
class TPE4(): pass
class TPOS(): pass
class TPUB(): pass
class TRCK(ID3NumericTextFrame): id = "TRCK"
class TDRA(): pass
class TRSN(): pass
class TRSO(): pass
class TSIZ(): pass
class TSRC(): pass
class TSSE(): pass
class TYER(ID3NumericTextFrame): id = "TYER"
class TXXX(ID3TextFrame):

    id = "TXXX"

    def __init__(self, desc, text):
        ID3TextFrame.__init__(self, text)
        self.desc = desc

    @property
    def packed_text(self):
        if not self.__packed_text:
            etext = self.text.encode(self.encodings(self.encoding))
            edesc = self.text.encode(self.encodings(self.encoding))
            self.__packed_text = pack(">%dsxx%ds" % (len(etext),
                                                     len(edesc)),
                                      etext, edesc)
        return self.__packed_text
class UFID(): pass
class USER(): pass
class USLT(): pass
class WCOM(): pass
class WCOP(): pass
class WOAF(): pass
class WOAR(): pass
class WOAS(): pass
class WORS(): pass
class WPAY(): pass
class WPUB(): pass
class WXXX(): pass
class XSOP(ID3TextFrame): id = "XSOP"
