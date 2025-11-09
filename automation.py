from typing import Tuple
import tkinter
import subprocess

from screenshot_processing import ScreenshotProcessor
from parser import Parser

from screencap import take_screenshot


class ActionAgent():
    def __init__(self, processor: ScreenshotProcessor, parser: Parser, folder: str):
        self.processor = processor
        self.parser = parser
        self.folder = folder

    def get_prompt_image_pair(self, processor: ScreenshotProcessor) -> Tuple[str]:
        screenshot_path = take_screenshot(self.folder)
        labeled_screenshot_path = processor.get_labeled_screenshot(screenshot_path)

        return screenshot_path, labeled_screenshot_path

    def parse_action_sequence(self, string: str) -> bool:
        return parser.parse_actions_string(string)

    def execute_action_sequence(self, string: str) -> bool:
        action_command, end_action = self.parse_action_sequence(string)

        subprocess.run(action_command.split())

        return end_action
    
    def complete_action_sequence(self, string: str):
        end_action = self.execute_action_sequence(string)
        
        if end_action:
            result = {
                "complete": True
            }
        else:
            screenshot_path, labeled_screenshot_path = self.get_prompt_image_pair(self.processor)
            result = {
                "complete": False,
                "screenshot_path": screenshot_path,
                "labeled_screenshot_path": labeled_screenshot_path
            }

        return result


if __name__ == "__main__":
    folder = 'screencaps'
    divisions = (30, 30)

    output_folder = 'labeled_screencaps'
    processor = ScreenshotProcessor(divisions, output_folder)

    root = tkinter.Tk()
    root.withdraw()
    img_shape = (root.winfo_screenheight(), root.winfo_screenwidth(), 3)
    parser = Parser(img_shape, divisions)

    action_agent = ActionAgent(processor, parser, folder)

