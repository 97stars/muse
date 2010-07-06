import os
import subprocess
import tempfile
import time

SUPPORTED_TARGETS = [".wav", ".flac", ".mp3"]
SUPPORTED_SOURCES = [".wav", ".flac"]


class UnsupportedTarget(Exception):
    pass


class UnsupportedSource(Exception):
    pass


def convert(source, target):
    # make sure everything is supported
    (_, s_extension) = os.path.splitext(source)
    (_, t_extension) = os.path.splitext(target)
    if s_extension not in SUPPORTED_SOURCES:
        raise UnsupportedSource("%s is an unsupported source" % s_extension)
    if t_extension not in SUPPORTED_TARGETS:
        raise UnsupportedTarget("%s is an unsupported target" % t_extension)

    tempf = _temp()
    _decode(source, tempf)
    if t_extension == ".wav":
        with open(target, "wb") as out:
            with open(tempf, "rb") as infile:
                out.write(infile.read())
    elif t_extension == ".flac":
        _flac(tempf, target)
    elif t_extension == ".mp3":
        _mp3(tempf, target)
    os.remove(tempf)


def _decode(filename, target):
    (_, extension) = os.path.splitext(filename)
    print "decoding %s..." % filename.encode("ascii", "replace")
    if extension == ".flac":
        with open(os.devnull, "wb") as nul:
            with open(filename, "rb") as source:
                subprocess.call(["flac", "-d", "-f", "-o", target, "-"],
                                stdin=source,
                                stdout=nul,
                                stderr=nul)
    else:
        with open(target, "wb") as out:
            with open(filename, "rb") as infile:
                out.write(infile.read())


def _flac(wavfile, filename):
    print "encoding %s..." % filename.encode("ascii", "replace")
    tempf = _temp()
    with open(os.devnull, "wb") as nul:
        subprocess.call(["flac", "--best", "-f", "-o", tempf, wavfile],
                        stdin=nul,
                        stdout=nul,
                        stderr=nul)
    print "saving %s..." & filename.encode("ascii", "replace")
    with open(filename, "wb") as out:
        with open(tempf, "rb") as temp:
            out.write(temp.read())
        _sync(out)
    os.remove(tempf)
    print "done!"


def _mp3(wavfile, filename):
    print "encoding %s..." % filename.encode("ascii", "replace")
    tempf = _temp()
    with open(os.devnull, "wb") as nul:
        subprocess.call(["lame", "-V0", "--replaygain-accurate", wavfile,
                         tempf],
                        stdin=nul,
                        stdout=nul,
                        stderr=nul)
    print "saving   %s..." % filename.encode("ascii", "replace")
    with open(filename, "wb") as out:
        with open(tempf, "rb") as temp:
            out.write(temp.read())
        _sync(out)
    os.remove(tempf)
    print "done!"


def _temp():
    (tempfh, tempname) = tempfile.mkstemp()
    os.close(tempfh)
    return tempname


def _sync(f):
    f.flush()
    os.fsync(f.fileno())
