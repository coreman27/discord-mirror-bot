import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
    print("Please ensure you have a .env file with GEMINI_API_KEY=your_key_here")
    exit(1)

print(f"Found API Key: {api_key[:4]}...{api_key[-4:]}")

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
    print("Gemini configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    exit(1)

# Generate dummy history (100 messages)
print("Generating dummy chat history (100 messages)...")
history = []
users = ["Alice", "Bob", "Charlie", "Dave", "Eve"]
for i in range(100):
    user = users[i % len(users)]
    message = f"This is message number {i+1}. We are talking about random things to test the API context window."
    history.append(f"{user}: {message}")

transcript = "\n".join(history)
target_user = "Bob"

prompt = (
    f"You are a savage roast master. Based on the following chat history, write a short, "
    f"biting, and funny roast targeting the user '{target_user}'. "
    f"Use the context of what they said or what others said to them. "
    f"Keep it under 280 characters. Do not be racist or overly offensive, just mean and funny.\n\n"
    f"Chat History:\n{transcript}"
)

print(f"Sending prompt with {len(transcript)} characters to Gemini...")

try:
    response = model.generate_content(prompt)
    print("\n--- Response from Gemini ---")
    print(response.text)
    print("----------------------------")
except Exception as e:
    print(f"\nError generating content: {e}")
