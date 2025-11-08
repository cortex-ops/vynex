from screencap import take_screenshot
from screenshot_processing import get_labeled_screenshot

def get_prompt_ready_pair() -> tuple[str]:
    screenshot_path = take_screenshot()
    labeled_screenshot_path = get_labeled_screenshot(screenshot_path)

    return screenshot_path, labeled_screenshot_path


if __name__ == "__main__":
    print(get_prompt_ready_pair())