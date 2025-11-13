import base64

from google.genai.types import File
from flask import Flask, request, jsonify
from flask_cors import CORS

# Assuming 'config.py' is in the same directory and has 'action_agent'
try:
    from config import action_agent
except ImportError:
    print("="*50)
    print("ERROR: Could not import 'action_agent' from 'config.py'.")
    print("Please make sure 'config.py' exists and is configured correctly.")
    print("="*50)
    # Define a dummy agent to allow the app to run for testing
    class DummyAgent:
        def run_llm_pipeline(self, *args):
            print("Using dummy action_agent.run_llm_pipeline")
            yield ("step1", "This is a dummy response.")
            yield ("step2", "Please check your config.py.")
    
    action_agent = DummyAgent()

app = Flask(__name__)
# Allow requests from your HTML file (which runs on a null origin)
CORS(app, resources={r"/chat": {"origins": "*"}}) 

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        
        user_text = data.get('text', '')
        file_data_b64 = data.get('file_data')
        file_mime_type = data.get('file_mime_type')
        
        prompt_parts = []
        
        # Add text part ONLY if it's not empty
        if user_text:
            prompt_parts.append(user_text)
            
        # Add file part
        if file_data_b64 and file_mime_type:
            try:
                # Decode the Base64 string to bytes
                if "text" in file_mime_type:
                    file_bytes = base64.b64decode(file_data_b64).decode()
                    prompt_parts.append(file_bytes)
                else:
                    file_bytes = base64.b64decode(file_data_b64)
                    prompt_parts.append(File(file_bytes))
                # Add to prompt parts as inline data
                # This is the correct structure: a dict, not a list
            except Exception as e:
                print(f"Error decoding base64 or handling file: {e}")
                # Don't stop, just report it in the response
                return jsonify({"response": f"Error processing file data: {e}"}), 400

        if not prompt_parts:
            # This happens if the user clicks send with no text and no file
            return jsonify({"response": "Please provide text or a file."}), 400

        # --- The Fix is Here ---
        # The frontend (script.js) expects a JSON object with a *string*
        # property called "response".
        # Your code was returning a list, which would look like "part1,part2"
        # in the chat window.
        # We will join the parts with newlines to create a single string.
        
        print(f"Calling action_agent with {len(prompt_parts)} parts.")
        response_parts = []
        # Your prompt_parts list is already in the correct format 
        # for the Gemini API. The error you saw was likely *inside* # your action_agent if it was wrapping prompt_parts in another list.
        for i in action_agent.run_llm_pipeline(prompt_parts):
            # Assuming i[1] is the string response part
            if isinstance(i, (list, tuple)) and len(i) > 1:
                response_parts.append(str(i[1]))
            else:
                # Handle if the pipeline returns something unexpected
                response_parts.append(str(i))

        result_string = "\n".join(response_parts)
        
        # Return the joined string as the response
        return jsonify({"response": result_string})
        
    except Exception as e:
        print(f"Error calling action_agent or Gemini API: {e}")
        # This will send the exact error message back to the frontend
        # so you can see it in the chat window, which is useful for debugging.
        return jsonify({"response": f"Backend Error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5000")
    print("Make sure 'config.py' is available and configured.")
    # Make it accessible on your network if needed, or just keep it local
    app.run(host='127.0.0.1', port=5000, debug=True)