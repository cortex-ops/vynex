import subprocess
import os
from datetime import datetime as dt

def get_root_path() -> str:
    '''
    Get the path of the file

    ### Returns
    - Root Path
    '''

    return '/'.join(__file__.split('/')[::-1][1:][::-1])

def get_screenshot_name() -> str:
    '''
    Get a valid name for the screenshot

    ### Returns
    - Name
        - format is YYYY-MM-DD HH:MM
    
    '''
    current_time =  str(dt.now())
    current_time_cleaned = current_time.split('.')[0].replace(':', '-').replace(' ', '_')

    result = current_time_cleaned + ".png"

    return result

def make_dir(pathname: str) -> None:
    '''
    make a directory, skips if already exists

    ### Parameters
    1. pathname: str
        - path of the directory
    
    ### Returns
    - None
    '''

    if not os.path.exists(pathname):
        os.mkdir(pathname)
        print(f'INFO: Directory {pathname} created')
    else:
        print(f'INFO: Directory {pathname} already exists, skipping...')

def make_dir_relative(pathname: str) -> None:
    '''
    make a directory from a relative pathname, skips if already exists

    ### Parameters
    1. pathname: str
        - path of the directory
    
    ### Returns
    - full path to the directory
    '''

    root_path = get_root_path()
    folder_path = f"{root_path}/{pathname}"

    make_dir(folder_path)

    return folder_path

def take_screenshot() -> str:
    '''
    Takes a screenshot and returns the path to it
    
    ### Returns
    - Path
    '''

    FOLDER = "screencaps"

    folder_path = make_dir_relative(FOLDER)
    screenshot_name = get_screenshot_name()
    screenshot_path = f'{folder_path}/{screenshot_name}'

    command = f'grim -t png {screenshot_path}'
    
    subprocess.run(command.split())

    return screenshot_path



if __name__ == "__main__":
    print(get_screenshot_name())
    print(get_root_path())
    print(take_screenshot())