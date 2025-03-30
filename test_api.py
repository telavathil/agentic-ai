import os
import time
import traceback
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("ANTHROPIC_API_KEY")

def test_api(max_retries=3):
    for attempt in range(max_retries):
        try:
            # Validate API key
            if not api_key or not api_key.startswith('sk-ant-'):
                raise ValueError("Invalid API key format")

            # Create the Anthropic client
            client = anthropic.Anthropic(api_key=api_key)

            # Attempt to create a message
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, can you confirm that the API is working?"
                    }
                ]
            )
            print("API Test Successful!")
            print("Response:", message.content[0].text)
            return True
        except anthropic.APIStatusError as e:
            if e.status_code == 529:  # Overloaded error
                print(f"API Overloaded (Attempt {attempt + 1}/{max_retries}):")
                print(f"Error: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                continue
            else:
                print("Unexpected API Error:")
                traceback.print_exc()
                return False
        except (ValueError, SyntaxError, TypeError) as e:
            print("API Test Failed:", str(e))
            traceback.print_exc()
            return False

    print("Max retries reached. API test failed.")
    return False

# Run the test
test_api()
