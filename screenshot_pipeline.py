from screencap import take_screenshot
from screenshot_processing import ScreenshotProcessor

def get_prompt_ready_pair(folder: str, processor: ScreenshotProcessor) -> tuple[str]:
    screenshot_path = take_screenshot(folder)
    labeled_screenshot_path = processor.get_labeled_screenshot(screenshot_path)

    return screenshot_path, labeled_screenshot_path


if __name__ == "__main__":
    divisions = (30, 30)
    folder = 'screencaps'
    output_folder = 'labeled_screencaps'
    processor = ScreenshotProcessor(divisions, output_folder)
    print(get_prompt_ready_pair(folder, processor))