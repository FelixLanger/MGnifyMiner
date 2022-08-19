from pathlib import Path
from typing import Optional, Union

import yaml


def _find_config_file() -> Union[Path, None]:
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
        return None


def load_config(config_file: Optional[Path] = None) -> dict:
    """
    Parse the yaml config_file into Python dictionary
    """
    if config_file is None:
        config_file = _find_config_file()
    if config_file is None:
        return {}
    with open(config_file) as configfile:
        cfg = yaml.load(configfile, Loader=yaml.CLoader)
    return cfg


config = load_config()
