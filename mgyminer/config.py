from pathlib import Path
from typing import Optional, Dict
import toml
from loguru import logger

config_template = {
        "Google service account json": "",
        "BigQuery project": "",
        "BigQuery Dataset": "",
        "MGnify 90 sequences": "",
        "MGnify sequences": ""
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


def save_config(new_config_data: Dict, save_to_home: bool = False) -> None:
    """
    Update the configuration file with new data.
    :param new_config_data: Dictionary containing new configuration data.
    :param save_to_home: Boolean indicating whether to save in the home directory or CWD.
    """
    filename = "miner.toml"
    config_path = Path.home() / filename if save_to_home else Path.cwd() / filename

    # Load existing configuration, if any
    existing_config = load_config(config_path) if config_path.exists() else {}

    # Update the existing configuration with new data
    updated_config = {**existing_config, **new_config_data}

    try:
        with open(config_path, 'w') as file:
            toml.dump(updated_config, file)
        logger.info(f"Config updated successfully at {config_path}")
    except Exception as e:
        logger.error(f"Failed to update config file: {e}")


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

def create_blank_config_template(config_path: Path) -> None:
    """
    Create a blank configuration template.
    """
    try:
        with open(config_path, 'w') as file:
            toml.dump(config_template, file)
        logger.info(f"Blank config template created at {config_path}")
    except Exception as e:
        logger.error(f"Failed to create config template: {e}")


def create_config(save_to_home: bool = False, use_user_input: bool = True) -> None:
    """
    Create a configuration file based on user input or as a blank template.
    :param save_to_home: Boolean indicating whether to save in the home directory or CWD.
    :param use_user_input: Boolean indicating whether to use user input or create a blank template.
    """
    filename = ".miner.toml"
    config_path = Path.home() / filename if save_to_home else Path.cwd() / filename

    if use_user_input:
        config_data = prompt_for_config()
        save_config(config_data, save_to_home)
    else:
        create_blank_config_template(config_path)


config = load_config()
