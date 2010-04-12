#!/usr/bin/env python
import sys
from optparse import OptionParser, make_option

from muse import Muse
from muse.tag.tag import AgnosticTags

USAGE = "usage: %prog [options] [INDIR [OUTDIR]]"

OPTION_LIST = [
    make_option("-o", "--output", action="store",
                type="string", dest="output", metavar="DIR"),
    make_option("-i", "--input", action="store",
                type="string", dest="input", metavar="GLOB"),
]

def parseopts():
    parser = OptionParser(option_list=OPTION_LIST, usage=USAGE)
    (options, args) = parser.parse_args()
    if not options.input: parser.error("input option is requred")
    if not options.output: parser.error("output option is required")
    if len(args) > 2: parser.error("too many positional args!")
    return (options, args)

def main():
    options, args = parseopts()
    i = "*.%s" % options.input # turn input into a glob
    o = ".%s" % options.output # turn output into an extension
    m = Muse(i, o)
    if len(args) == 2:
        m.go(unicode(args[0]), unicode(args[1]))
    elif len(args) == 0:
        m.go(u".")
    else:
        m.go(unicode(args[0]))

if __name__ == '__main__':
    main()
