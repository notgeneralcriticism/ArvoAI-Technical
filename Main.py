import openai
import os
from dotenv import load_dotenv

load_dotenv()

model = "gpt-3.5-turbo"

# Function to parse natural language input using GPT
def parse_with_gpt(input_text, model_in):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"Extract the framework, database, and cloud provider from the following text:\n{input_text}"

    response = openai.ChatCompletion.create(
        model=model_in,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the response content
    parsed_data = response['choices'][0]['message']['content']
    return parsed_data

# Example Usage
input_text = "Deploy a Flask app with PostgreSQL on AWS."
parsed_requirements = parse_with_gpt(input_text, model)
print(parsed_requirements)