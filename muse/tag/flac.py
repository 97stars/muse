import os

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
            # v_string = unpack("%ds" % v_length, f.read(v_length))[0]
            f.seek(v_length, os.SEEK_CUR)
            num_comments = unpack("<I", f.read(4))[0]
            for _ in xrange(num_comments):
                c_length = unpack("<I", f.read(4))[0]
                c_data = unpack("%ds" % c_length, f.read(c_length))[0]
                yield _parse_comment(c_data.decode("utf-8"))


def save(tags, filename):
    with open(filename, "rb") as f:
        if not _is_flac(f):
            raise ValueError("%s is not a flac file" %
                             filename.encode("ascii", "replace"))
        filedata, blocks = _load_file(f)
    vendor_string = u"tneudoerffer's muse".encode("utf-8")
    vendor_length = len(vendor_string)
    comments = []
    comment_block = {}
    for k in tags:
        text = (k + u"=" + tags[k]).encode("utf-8")
        comment = pack("<I", len(text))
        comment += pack("%ds" % len(text), text)
        comments.append(comment)
    packed_comments = "".join(comments)
    comment_block['data'] = pack("<I", vendor_length)
    comment_block['data'] += pack("%ds" % len(vendor_string), vendor_string)
    comment_block['data'] += pack("<I", len(comments))
    comment_block['data'] += pack("%ds" % len(packed_comments),
                                  packed_comments)
    comment_block['type'] = 4
    comment_block['length'] = len(comment_block['data'])
    with open(filename, "wb") as f:
        f.write("fLaC")
        for block in blocks:
            if block['type'] == 0:
                # streaminfo gets written first
                f.write(_pack_block(block))
            elif block['type'] != 4 and block['type'] != 1:
                # don't write any existing vorbis comments
                # and don't write padding
                f.write(_pack_block(block))
        f.write(_pack_block(comment_block, True))
        f.write(filedata)


def _is_flac(fh):
    return unpack("4s", fh.read(4))[0] == "fLaC"


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
        block['type'] = (header >> 24) & 0x7F
        block['length'] = header & 0xFFFFFF
        block['data'] = fh.read(block['length'])
        blocks.append(block)
    filedata = fh.read()
    return (filedata, blocks)


def _parse_comment(string):
    if "=" not in string:
        raise ValueError("%s doesn't appear to be a comment" %
                         string.encode("ascii", "replace"))
    return tuple(string.split("=", 1))
