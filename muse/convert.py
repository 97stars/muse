import os
import subprocess
import sys
import tempfile
import time

SUPPORTED_TARGETS = [".wav", ".flac", ".mp3"]
SUPPORTED_SOURCES = [".wav", ".flac"]

class UnsupportedTarget(Exception): pass
class UnsupportedSource(Exception): pass

def convert(source, target):
    # make sure everything is supported
    (_, s_extension) = os.path.splitext(source)
    (_, t_extension) = os.path.splitext(target)
    if s_extension not in SUPPORTED_SOURCES:
        raise UnsupportedSource("%s is an unsupported source" % s_extension)
    if t_extension not in SUPPORTED_TARGETS:
        raise UnsupportedTarget("%s is an unsupported target" % t_extension)

    inpipe = _decode(source)
    if t_extension == ".wav":
        with open(target) as out:
            out.write(inpipe.read())
    elif t_extension == ".flac":
        _flac(inpipe, target)
    elif t_extension == ".mp3":
        _mp3(inpipe, target)

def _decode(filename):
    (_, extension) = os.path.splitext(filename)
    print "decoding %s..." % filename.encode("ascii", "replace")
    with open(filename, "rb") as f:
        if extension == ".flac":
            p = subprocess.Popen(["flac", "-d", "--stdout", "-"],
                                 stdin=f,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            return p.stdout
        else:
            return f

def _flac(inpipe, filename):
    print "encoding %s..." % filename.encode("ascii", "replace")
    with open(filename, "wb") as out:
        p = subprocess.Popen(["flac", "--best", "--stdout", "-"],
                             stdin=inpipe,
                             stdout=out,
                             stderr=subprocess.PIPE)
        p.communicate()
        _sync(out)
    print "done!"

def _mp3(inpipe, filename):
    print "encoding %s..." % filename.encode("ascii", "replace")
    (tempfh, tempname) = tempfile.mkstemp()
    os.close(tempfh)
    p = subprocess.Popen(["lame", "-V0", "--replaygain-accurate", "-", tempname],
                         stdin=inpipe,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.communicate()
    print "saving   %s..." % filename.encode("ascii", "replace")
    with open(filename, "wb") as out:
        with open(tempname, "rb") as temp:
            out.write(temp.read())
        _sync(out)
    os.remove(tempname)
    print "done!"

def _sync(f):
    f.flush()
    os.fsync(f.fileno())
