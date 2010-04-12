import os
from struct import pack, unpack

class ID3Error(Exception): pass
class ID3FrameUnsupported(Exception): pass

VERSION = (3, 0) # ID3v2 version
ENCODINGS = {
    0: "iso-8859-1",
    1: "UTF-16" }

def save(framelist, filename):
    filedata = _load_file(filename)
    framedata = "".join(_pack_frames(framelist))
    header = _id3_header(len(framedata))
    with open(filename, "wb") as f:
        f.write(header)
        f.write(framedata)
        f.write(filedata)

def _load_file(filename):
    if not os.path.exists(filename): return ""
    with open(filename, "rb") as f:
        seek = 0
        if _is_id3(f):
            f.seek(6, os.SEEK_SET)
            seek = _unpack_id3_size(unpack(">BBBB", f.read(4)))
        f.seek(seek, os.SEEK_SET)
        return f.read()

def _is_id3(fh):
    fh.seek(0, os.SEEK_SET)
    ident = unpack(">3s", fh.read(3))[0]
    return ident == "ID3"

def _pack_frames(framelist):
    def packframe(frame):
        if frame["ID"] == "TXXX":
            desc = frame["DESC"].encode(ENCODINGS[frame["ENCODING"]])
            text = frame["TEXT"].encode(ENCODINGS[frame["ENCODING"]])
            frametext = pack(">B", frame["ENCODING"])
            frametext += pack(">%dsxx%ds" % (len(desc), len(text)),
                              desc, text)
        elif frame["ID"][0] == "T":
            text = frame["TEXT"].encode(ENCODINGS[frame["ENCODING"]])
            frametext = pack(">B", frame["ENCODING"])
            frametext += pack(">%ds" % len(text), text)
        framedata = pack(">4s", frame["ID"])
        framedata += pack(">I", len(frametext))
        framedata += pack(">H", 0) # flags
        framedata += frametext
        return framedata
    return [packframe(x) for x in framelist]

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

def _generic_text(ident, text):
    return {
        "ID": ident,
        "ENCODING": 1,
        "TEXT": text }

def _numeric_text(ident, text):
    return {
        "ID": ident,
        "ENCODING": 0,
        "TEXT": text }

def AENC(): _unsupported()
def APIC(): _unsupported()
def COMM(): _unsupported()
def COMR(): _unsupported()
def ENCR(): _unsupported()
def EQUA(): _unsupported()
def ETCO(): _unsupported()
def GEOB(): _unsupported()
def GRID(): _unsupported()
def IPLS(): _unsupported()
def LINK(): _unsupported()
def MCDI(): _unsupported()
def MLLT(): _unsupported()
def OWNE(): _unsupported()
def PRIV(): _unsupported()
def PCNT(): _unsupported()
def POPM(): _unsupported()
def POSS(): _unsupported()
def RBUF(): _unsupported()
def RVAD(): _unsupported()
def RVRB(): _unsupported()
def SYLT(): _unsupported()
def SYTC(): _unsupported()
def TALB(text):
    return _generic_text("TALB", text)
def TBPM(): _unsupported()
def TCOM(): _unsupported()
def TCON(): _unsupported()
def TCOP(): _unsupported()
def TDAT(): _unsupported()
def TDLY(): _unsupported()
def TENC(): _unsupported()
def TEXT(): _unsupported()
def TFLT(): _unsupported()
def TIME(): _unsupported()
def TIT1(text):
    return _generic_text("TIT1", text)
def TIT2(text):
    return _generic_text("TIT2", text)
def TIT3(text):
    return _generic_text("TIT3", text)
def TKEY(): _unsupported()
def TLAN(): _unsupported()
def TLEN(): _unsupported()
def TMED(): _unsupported()
def TOAL(): _unsupported()
def TOFN(): _unsupported()
def TOLY(): _unsupported()
def TOPE(): _unsupported()
def TORY(): _unsupported()
def TOWN(): _unsupported()
def TPE1(text):
    return _generic_text("TPE1", text)
def TPE2(text):
    return _generic_text("TPE2", text)
def TPE3(): _unsupported()
def TPE4(): _unsupported()
def TPOS(): _unsupported()
def TPUB(): _unsupported()
def TRCK(text):
    return _numeric_text("TRCK", text)
def TDRA(): _unsupported()
def TRSN(): _unsupported()
def TRSO(): _unsupported()
def TSIZ(): _unsupported()
def TSRC(): _unsupported()
def TSSE(): _unsupported()
def TYER(text):
    return _numeric_text("TYER", text)
def TXXX(desc, text):
    frame = _generic_text("TXXX", text)
    frame["DESC"] = desc
    return frame
def UFID(): _unsupported()
def USER(): _unsupported()
def USLT(): _unsupported()
def WCOM(): _unsupported()
def WCOP(): _unsupported()
def WOAF(): _unsupported()
def WOAR(): _unsupported()
def WOAS(): _unsupported()
def WORS(): _unsupported()
def WPAY(): _unsupported()
def WPUB(): _unsupported()
def WXXX(): _unsupported()

def _unsupported():
    raise ID3FrameUnsupported()
