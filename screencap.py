import subprocess
import os
from datetime import datetime as dt
from typing import List

def get_root_path() -> str:
    """
    Get the absolute path to the directory containing this script.
    
    Uses __file__ to determine the script's location and parses the
    parent directory.

    Returns:
        The absolute path to the script's parent directory.
    """
    script_path = os.path.abspath(__file__)
    return os.path.dirname(script_path)

def get_screenshot_name() -> str:
    """
    Generates a timestamped filename for a screenshot.
    
    The format is 'YYYY-MM-DD_HH-MM-SS.png'.

    Returns:
        A string formatted as a unique, timestamped PNG filename.
    """
    current_time = str(dt.now())
    current_time_cleaned = current_time.split('.')[0].replace(':', '-').replace(' ', '_')
    result = current_time_cleaned + ".png"
    return result

def make_dir(pathname: str) -> None:
    """
    Creates a directory if it does not already exist.
    
    Prints an informational message about creation or skipping.

    Args:
        pathname: The absolute path of the directory to create.
    """
    if not os.path.exists(pathname):
        os.mkdir(pathname)
        print(f'INFO: Directory {pathname} created')
    else:
        print(f'INFO: Directory {pathname} already exists, skipping...')

def make_dir_relative(pathname: str) -> str:
    """
    Creates a directory relative to this script's location.

    Args:
        pathname: The relative path of the directory (e.g., "screencaps").

    Returns:
        The full, absolute path to the created or existing directory.
    """
    root_path = get_root_path()
    folder_path = os.path.join(root_path, pathname)
    make_dir(folder_path)
    return folder_path

def take_screenshot() -> str:
    """
    Takes a screenshot using 'grim' and saves it to a 'screencaps' folder.
    
    Orchestrates directory creation, name generation, and executing
    the shell command.

    Returns:
        The absolute path to the newly created screenshot file.
    """
    FOLDER = "screencaps"
    folder_path = make_dir_relative(FOLDER)
    screenshot_name = get_screenshot_name()
    screenshot_path = os.path.join(folder_path, screenshot_name)

    command: List[str] = ['grim', '-t', 'png', screenshot_path]
    
    subprocess.run(command)

    return screenshot_path


if __name__ == "__main__":
    print(f"Root path: {get_root_path()}")
    print(f"Generated name: {get_screenshot_name()}")
    saved_path = take_screenshot()
    print(f"Screenshot saved to: {saved_path}")