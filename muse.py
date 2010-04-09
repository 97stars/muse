#!/usr/bin/env python
import sys
from optparse import OptionParser, make_option

from muse import Muse
from muse.tag.tag import AgnosticTags

USAGE = "usage: %prog -d DIR -i GLOB -t EXTENSION [options]"

OPTION_LIST = [
    make_option("-o", "--output", action="store",
                type="string", dest="output", metavar="DIR"),
    make_option("-d", "--directory", action="store",
                type="string", dest="dir", metavar="DIR"),
    make_option("-i", "--input", action="store",
                type="string", dest="input", metavar="GLOB"),
    make_option("-t", "--out-type", action="store",
                type="string", dest="type", metavar="EXTENSION"),
]

def parseopts():
    parser = OptionParser(option_list=OPTION_LIST)
    (options, args) = parser.parse_args()
    if not options.dir: parser.error("directory option is required")
    if not options.input: parser.error("input option is requred")
    if not options.type: parser.error("type option is required")
    if len(args) != 0: parser.error("I take no positional args!")
    return options

def main():
    options = parseopts()
    m = Muse(options.input, options.type)
    if options.output:
        m.go(options.dir, options.output)
    else:
        m.go(options.dir)

if __name__ == '__main__':
    main()
