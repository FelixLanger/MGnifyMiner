from pathlib import Path
from typing import Optional, Dict
import toml
from loguru import logger

config_template = {
    "Google service account json": "",
    "BigQuery project": "",
    "BigQuery Dataset": "",
    "MGnify 90 sequences": "",
    "MGnify sequences": "",
}


def _find_config_file() -> Optional[Path]:
    """
    Search through directories for mgyminer config file.
    Files are used by descending priority:
        - miner.toml in current working directory
        - .miner.toml in current working directory
        - miner.toml in $HOME directory
        - .miner.toml in $HOME directory (dotfile)
    :return: Path to config_file or None if not found
    """
    paths = [
        Path("miner.toml"),
        Path(".miner.toml"),
        Path.home() / "miner.toml",
        Path.home() / ".miner.toml",
    ]
    return next((path for path in paths if path.exists()), None)


def load_config(config_file: Optional[Path] = None) -> dict:
    """
    Parse the toml config_file into Python dictionary.
    :param config_file: Optional path to the config file
    :return: Config dictionary or empty dict if unable to load
    """
    if config_file is None:
        config_file = _find_config_file()

    if config_file is None:
        logger.warning("Config file not found.")
        return {}

    try:
        with open(config_file, "r") as configfile:
            return toml.load(configfile)
    except Exception as e:
        logger.error(f"Failed to load config file: {e}")
        return {}


def prompt_for_config() -> Dict:
    """
    Prompt the user for configuration values.
    """
    print("Please enter the configuration values (press Enter to skip):")
    user_config = {}
    for key in config_template:
        user_input = input(f"{key}: ")
        if user_input:  # Only add entry if user provided a value
            user_config[key] = user_input
    return user_config


def save_config(
    new_config_data: Optional[Dict] = None,
    save_to_home: bool = False,
    blank: bool = False,
) -> None:
    """
    Create or update the configuration file with new data.
    :param new_config_data: Optional dictionary containing new configuration data.
    :param save_to_home: Boolean indicating whether to save in the home directory or CWD.
    :param blank: Boolean indicating whether to create a blank configuration file.
    """
    filename = ".miner.toml"
    config_path = Path.home() / filename if save_to_home else Path.cwd() / filename

    if blank:
        config_data = config_template
    else:
        # Load existing configuration, if any, and update with new data
        existing_config = load_config(config_path) if config_path.exists() else {}
        config_data = {**existing_config, **(new_config_data or {})}

    try:
        with open(config_path, "w") as file:
            toml.dump(config_data, file)
        logger.info(
            f"Config {'created' if blank else 'updated'} successfully at {config_path}"
        )
        print(
            f"Config {'created' if blank else 'updated'} successfully at {config_path}"
        )
    except Exception as e:
        logger.error(f"Failed to {'create' if blank else 'update'} config file: {e}")


def config_cli(args):
    """
    CLI handler for creating or updating the configuration file.
    """
    if args.blank:
        save_config(save_to_home=args.project, blank=True)
    else:
        user_config = prompt_for_config()
        save_config(user_config, save_to_home=args.project)
