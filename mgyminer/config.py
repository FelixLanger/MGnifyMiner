import sys
from pathlib import Path

import yaml


def find_config_file() -> Path:
    """
    Search through directories for mgyminer config file.
    Files are used by descending priority:
        - mgyminer.yaml in current working directory
        - .mgyminer.yaml in $HOlME directory (dotfile)
    :return: Path to config_file
    """
    paths = list(
        filter(
            lambda x: x.exists(),
            [Path() / "mgyminer.yaml", Path.home() / ".mgyminer.yaml"],
        )
    )

    if paths:
        return paths[0]
    else:
        sys.exit("Exited\nCoun't find mgyminer.yaml config file")


def parse_config(config_file: Path) -> dict:
    """
    Parse the yaml config_file into Python dirctionary
    """
    with open(config_file) as configfile:
        cfg = yaml.load(configfile, Loader=yaml.CLoader)
    return cfg


config = parse_config(find_config_file())
