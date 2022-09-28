import hashlib


def get_file_hash(file, ignore_comments=True):
    """
    Get the md5 hash of file without the # commented lines
    :param ignore_comments: choose if lines commented out with # should be ignored
    :param file: file to hash
    :return: md5 hash digest
    """
    md5 = hashlib.md5()
    with open(file, "rt") as fin:
        if ignore_comments:
            for line in fin.readlines():
                if not line.startswith("#"):
                    md5.update(line.encode("utf-8"))
        else:
            for line in fin.readlines():
                md5.update(line.encode("utf-8"))

    return md5.hexdigest()
