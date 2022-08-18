import hashlib


def get_file_hash(file):
    """
    Get the md5 hash of file without the # commented lines
    :param file: file to hash
    :return: md5 hash digest
    """
    md5 = hashlib.md5()
    with open(file, "rt") as fin:
        for line in fin.readlines():
            if not line.startswith("#"):
                md5.update(line.encode("utf-8"))
    return md5.hexdigest()
