import tkinter

from screenshot_processing import ScreenshotProcessor
from automation import ActionAgent
from parser import Parser
from llm_api_handler import LLMInterface

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