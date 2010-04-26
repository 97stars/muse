import re


BAD_CHARS = r"[\/:*?\"<>|]"


def sanitize(string):
    s = re.sub("\.$", "_", string)
    s = re.sub("^\.", "_", s)
    return re.sub(BAD_CHARS, "_", s)
