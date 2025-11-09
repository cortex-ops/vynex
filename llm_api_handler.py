from google import generativeai
from PIL import Image
import os
from dotenv import load_dotenv

class LLMInterface:
    def __init__(self, model_name: str, system_prompt_file: str):
        self.model_name = model_name
        self._configure_api()
        
        system_prompt = self._load_system_prompt(system_prompt_file)
        self.model = self._initialize_model(system_prompt)
        print("LLMInterface initialized successfully.")

    def _configure_api(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        generativeai.configure(api_key=api_key)
        print("API configured.")

    def _load_system_prompt(self, filepath: str) -> str:
        print(f"Loading system prompt from '{filepath}'...")
        with open(filepath, 'r') as f:
            return f.read()


    def _initialize_model(self, system_prompt: str) -> generativeai.GenerativeModel:
        """Initializes the GenerativeModel with system instructions."""
        
        generation_config = {
            "response_mime_type": "text/plain",
        }

        print(f"Initializing model: {self.model_name}...")
        model = generativeai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt,
            generation_config=generation_config
        )
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

        response = self.model.generate_content(prompt_parts)
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