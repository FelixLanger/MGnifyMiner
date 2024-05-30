import hashlib


def calculate_text_md5(file, ignore_comments=True):
    """
    Get the md5 hash of content in a file without the # commented lines
    :param ignore_comments: choose if lines commented out with # should be ignored
    :param file: file to hash
    :return: md5 hash digest
    """
    md5 = hashlib.md5()
    with open(file) as fin:
        if ignore_comments:
            for line in fin.readlines():
                if not line.startswith("#"):
                    md5.update(line.encode("utf-8"))
        else:
            for line in fin.readlines():
                md5.update(line.encode("utf-8"))

    return md5.hexdigest()


def calculate_md5(file_path):
    """
    calculate the md5 hash of a file
    Args:
        file_path: Path to file

    Returns: md5sum
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()
