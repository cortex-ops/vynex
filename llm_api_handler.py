# from google import generativeai
from google import genai
from PIL import Image
import os
from dotenv import load_dotenv

class LLMInterface:
    def __init__(self, model_name: str, system_prompt_file: str, include_thinking: bool = True):
        self._configure_api()
        
        system_prompt = self._load_system_prompt(system_prompt_file)
        generation_config = genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=genai.types.ThinkingConfig(
                include_thoughts=include_thinking
            )
        )
        
        try:
            self.model = self._initialize_model()
        except ValueError:
            print("API key not found, please make you have a .env file with GEMINI_API_KEY=<your api key>")

        self.chat = self.model.chats.create(
            model=model_name,
            config=generation_config
        )
        
        print("LLMInterface initialized successfully.")


    def _configure_api(self):
        load_dotenv('.env')
        print("API configured.")

    def _load_system_prompt(self, filepath: str) -> str:
        print(f"Loading system prompt from '{filepath}'...")
        with open(filepath, 'r') as f:
            return f.read()


    def _initialize_model(self) -> genai.Client:
        """Initializes the GenerativeModel with system instructions."""

        print(f"Initializing client")
        model = genai.Client()
        print("Model initialized.")
        return model

    def get_action(self, user_goal: str, original_image_path: str, labeled_image_path: str) -> str:
        print(f"\n--- Sending new task to Gemini ---")
        print(f"Goal: {user_goal}")

        task_prompt = user_goal

        img_orig = Image.open(original_image_path)
        img_labeled = Image.open(labeled_image_path)
        print(f"Loaded images: '{original_image_path}', '{labeled_image_path}'")

        prompt_parts = [task_prompt, img_orig, img_labeled]

        response = self.chat.send_message(prompt_parts)
        return response.text

if __name__ == "__main__":
    MODEL_NAME = "gemini-2.5-flash"
    SYSTEM_PROMPT_FILE = "help/prompt.txt"

    # 1. Initialize the class (happens once)
    llm_agent = LLMInterface(
        model_name=MODEL_NAME,
        system_prompt_file=SYSTEM_PROMPT_FILE
    )

    # 2. --- SIMULATE FIRST TASK ---
    goal_1 = "Click 'File' at 15"
    action_list_str_1 = llm_agent.get_action(
        user_goal=goal_1,
        original_image_path="image_original.png",
        labeled_image_path="image_labeled.png"
    )
    print("\n--- Model Response (Task 1) ---")
    print(action_list_str_1)

    # 3. --- SIMULATE SECOND TASK (VERIFICATION) ---
    goal_2 = "Type 'Hello' in box 380."
    print("\n(Simulating a new request where the goal is already met...)")
    action_list_str_2 = llm_agent.get_action(
        user_goal=goal_2,
        original_image_path="image_original.png",
        labeled_image_path="image_labeled.png"
    )
    print("\n--- Model Response (Task 2 - Goal Met) ---")
    print(action_list_str_2)