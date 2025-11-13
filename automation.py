from typing import Tuple, Generator, Any
import tkinter
import time
import os
import subprocess

from screenshot_processing import ScreenshotProcessor
from parser import Parser
from llm_api_handler import LLMInterface

from screencap import take_screenshot


class ActionAgent():
    def __init__(self, processor: ScreenshotProcessor, parser: Parser, llm_interface: LLMInterface, folder: str):
        self.processor = processor
        self.parser = parser
        self.llm_interface = llm_interface
        self.folder = folder

        self.past_screenshots = []

    def get_prompt_image_pair(self) -> Tuple[str]:
        screenshot_path = take_screenshot(self.folder)
        labeled_screenshot_path = self.processor.get_labeled_screenshot(screenshot_path)

        return screenshot_path, labeled_screenshot_path

    def parse_action_sequence(self, string: str) -> Tuple[str, bool]:
        return self.parser.parse_actions_string(string)

    def execute_action_sequence(self, string: str) -> bool:
        action_command, end_action = self.parse_action_sequence(string)

        print(f"running command chain: {action_command}")
        subprocess.run(action_command, shell=True)

        return end_action
    
    def complete_action_sequence(self, string: str) -> bool:
        string = string.strip().strip('`')
        print(f"current sequence: {string}")
        end_action = self.execute_action_sequence(string)
        return end_action
    
    def run_llm_prompt(self, user_goal: list) -> Tuple[str, bool, str]:
        # delete past screenshots
        for image in self.past_screenshots:
            os.remove(image)
            self.past_screenshots.remove(image)

        screenshot_path, labeled_screenshot_path = self.get_prompt_image_pair()
        self.past_screenshots.append(screenshot_path)
        self.past_screenshots.append(labeled_screenshot_path)
        
        action_sequence, thought_summary = self.llm_interface.get_action(user_goal, screenshot_path, labeled_screenshot_path)
        end_action = self.complete_action_sequence(action_sequence)

        return action_sequence, end_action, thought_summary
    
    def run_llm_pipeline(self, user_goal: list, wait_time: int = 2) -> Generator[tuple[str, str], Any, None]:
        end_action = False
        sequences = []
        og_goal = user_goal[0]
        while not end_action:
            time.sleep(wait_time)
            if isinstance(og_goal, str):
                new_prompt = f"The original task is {og_goal} Your previous instructions were \n{('\n'.join(sequences)) or "None"} \n Here are the new screenshots, continue"
                new_user_goal = [new_prompt, *user_goal[1:]]

            action_sequence, end_action, thought_summary = self.run_llm_prompt(new_user_goal)
            sequences.append(action_sequence)

            yield action_sequence, thought_summary

if __name__ == "__main__":
    folder = 'screencaps'
    divisions = (25, 25)

    output_folder = 'labeled_screencaps'
    processor = ScreenshotProcessor(divisions, output_folder)

    root = tkinter.Tk()
    root.withdraw()
    img_shape = (root.winfo_screenheight(), root.winfo_screenwidth(), 3)
    parser = Parser(img_shape, divisions)

    model_name = "gemini-2.5-flash"
    prompt_file = "help/prompt.txt"
    llm_interface = LLMInterface(model_name, prompt_file)

    action_agent = ActionAgent(processor, parser, llm_interface, folder)

    action_agent.run_llm_pipeline(input("Enter prompt: "))
