## NPL Inits ##
import openai
import os
from dotenv import load_dotenv

## Github Analysis ##
from git import Repo
from collections import Counter
from pathlib import Path


##### NPL #####
# load .env file containing all the API keys
load_dotenv() 

# define the gpt model
model = "gpt-3.5-turbo"

# Function to parse natural language input using GPT
def parse_with_gpt(input_text, model_in):
    openai.api_key = os.getenv("OPENAI_API_KEY") # pass api key

    # initialize prompt
    prompt = f"Extract the framework, database, and cloud provider from the following text:\n{input_text}"

    # receive response
    response = openai.ChatCompletion.create(
        model=model_in,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the response content
    parsed_data = response['choices'][0]['message']['content']
    return parsed_data

'''
# test
input_text = "Deploy a Flask app with PostgreSQL on AWS."
parsed_requirements = parse_with_gpt(input_text, model)
print(parsed_requirements)
'''

##### ANALYZE GIT REPOS #####
# if local directory containing repo DNE, create a new folder and clone repo
def clone_or_open_repo(repo_url, local_dir):
    if not os.path.exists(local_dir):
        print(f"Cloning repository from {repo_url}...")
        Repo.clone_from(repo_url, local_dir)
    else:
        print(f"Repository already exists at {local_dir}.")
    return Repo(local_dir)

# Analyze the repo and collect information on languages and frameworks
def detect_languages_and_frameworks(repo_path):
    language_counter = Counter()
    framework_info = {}

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix

            # Detect language based on file extensions
            if ext in {".py", ".java", ".js", ".ts", ".rb"}:
                language_counter[ext] += 1
            
            # Framework detection based on specific files
            if file == "requirements.txt":
                framework_info["Python"] = "Detected via requirements.txt"
            elif file == "package.json":
                framework_info["Node.js"] = "Detected via package.json"
            elif file == "pom.xml":
                framework_info["Java (Maven)"] = "Detected via pom.xml"
            elif file == "Dockerfile":
                framework_info["Docker"] = "Detected via Dockerfile"
            elif file.endswith(".yml") or file.endswith(".yaml"):
                framework_info["YAML Configuration"] = f"Detected via {file}"

    return language_counter, framework_info

# Example Usage
repo_url = "https://github.com/Arvo-AI/hello_world.git"
local_dir = "local_repo"

# Clone or open repository
repo = clone_or_open_repo(repo_url, local_dir)

# Analyze repository
languages, frameworks = detect_languages_and_frameworks(local_dir)

# print results of the detected languages
print("Detected Languages:")
for lang, count in languages.items():
    print(f"{lang}: {count} file(s)")

# print results of detected frameworks
print("\nDetected Frameworks:")
for framework, detail in frameworks.items():
    print(f"{framework}: {detail}")

##### TERRAFORM #####