
import openai
import os
from dotenv import load_dotenv
from git import Repo
import zipfile
from collections import Counter
from pathlib import Path
import subprocess
import json
from typing import Dict, Any 


##### SECTION 1: NPL #####

# define the gpt model
model = "gpt-3.5-turbo"

# load .env file containing all the API keys
load_dotenv() 

# Function to parse natural language input using GPT
def parse_with_gpt(input_text, model_in):
    
    openai.api_key = os.getenv("OPENAI_API_KEY") # pass api key

    # initialize prompt
    prompt = f"Extract the framework, database, and cloud provider (abbrev.) from the following text:\n{input_text}. Provide answers in .json format"
    
    # receive response
    response = openai.ChatCompletion.create(
        model=model_in,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract the response content
    parsed_data = response["choices"][0]["message"]["content"]
    
    # Convert response to structured format (JSON or dict)
    try:
        return json.loads(parsed_data)
    except json.JSONDecodeError:
        return {"error": "Failed to parse GPT output."}

''' 
#test
input = "Deploy this Flask application on AWS"
response = parse_with_gpt(input, model)
print(response)
'''

##### SECTION 2: ANALYZE GIT REPOS #####
# if local directory containing repo DNE, create a new folder and clone repo or extract zip-file
def clone_or_open_repo(repo_url=None, local_dir=None, zip_file=None):
    if zip_file:
    # If a zip file is provided, extract it to the local directory
        if not os.path.exists(local_dir):
            print(f"Extracting zip file to {local_dir}...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(local_dir)
            print(f"Extraction complete.")
        else:
            print(f"Directory already exists at {local_dir}. Skipping extraction.")
        return None  # No Repo object for zip file

    elif repo_url:
        # If a repository URL is provided, clone it
        if not os.path.exists(local_dir):
            print(f"Cloning repository from {repo_url}...")
            Repo.clone_from(repo_url, local_dir)
        else:
            print(f"Repository already exists at {local_dir}.")
        return Repo(local_dir)  # Return the Repo object for a Git repo
    
    else:
        raise ValueError("Either 'repo_url' or 'zip_file' must be provided.")


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
            '''
            elif ext == ".html":
                language_counter["HTML"] += 1
            elif ext == ".css":
                language_counter["CSS"] += 1
            '''

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

    return {"languages": language_counter, "frameworks": framework_info}

##### SECTION 3: TERRAFORM AND DEPLOYMENT #####

# Function to generate Terraform configuration dynamically for GCP
def generate_terraform_config(parsed_data: Dict[str, Any], repo_analysis: Dict[str, Any]):
       
    cloud_provider = parsed_data.get("cloud_provider", "aws").lower()
    app_type = parsed_data.get("framework", "unknown")

    # Example Terraform configurations for AWS and GCP
   
    if cloud_provider == "gcp":
        terraform_config = f"""
        provider "google" {{
            project = "arvoaitechnical"
            region  = "us-central1-a"
            credentials = file("application_default_credentials.json")
        }}

        resource "google_compute_instance" "app" {{
            name         = "arvoaitech"
            machine_type = "e2-micro"
            zone         = "us-central1-a"

            boot_disk {{
                initialize_params {{
                    image = "projects/debian-cloud/global/images/family/debian-11"
                }}
            }}

            network_interface {{
                network = "default"
                access_config {{}}
            }}

            metadata_startup_script = <<-EOT
            #!/bin/bash
            apt-get update
            apt-get install -y python3-pip git
            git clone https://github.com/Arvo-AI/hello_world.git /app
            cd /app
            pip3 install -r requirements.txt
            python3 app.py

            # Serve HTML/CSS files
            # cp -r /app/static/* /var/www/html/
            # systemctl restart nginx
            
            EOT
        }}
            output "vm_public_ip" {{
                value = google_compute_instance.app.network_interface[0].access_config[0].nat_ip
            }}
        """
    elif cloud_provider == "aws":
        terraform_config = f"""
        provider "aws" {{
            region = "us-east-2"
        }}

        resource "aws_instance" "app" {{
            ami           = "ami-0c55b159cbfafe1f0"  # Amazon Linux 2
            instance_type = "t2.micro"

            tags = {{
                Name = "autodeploy-app"
            }}

            user_data = <<-EOT
            #!/bin/bash
            sudo yum update -y
            sudo yum install -y git python3
            git clone https://github.com/Arvo-AI/hello_world.git /home/ec2-user/app
            cd /home/ec2-user/app
            python3 -m pip install -r requirements.txt
            python3 app.py

            # Serve HTML/CSS files
            # cp -r /home/ec2-user/app/static/* /usr/share/nginx/html/
            # systemctl restart nginx

            EOT
        }}
        """
    else:
        raise ValueError(f"Unsupported cloud provider: {cloud_provider}")

    # Save configuration to Terraform file
    with open("main.tf", "w") as tf_file:
        tf_file.write(terraform_config)


def apply_terraform():
    """
    Apply the Terraform configuration to provision resources.
    """
    # Step 0: Destroy Terraform Instances

    try:
        subprocess.run(["terraform", "init"], check=True)
       
        print("Checking and destroying existing resources...")
        subprocess.run(["terraform", "destroy", "-auto-approve"], check=False)
       
        print("Applying Terraform configuration...")
        subprocess.run(["terraform", "apply", "-auto-approve"], check=True)

        # Retrieve the VM's public IP using terraform output
        result = subprocess.run(
            ["terraform", "output", "-raw", "vm_public_ip"],
            capture_output=True,
            text=True,
            check=True
        )
        vm_public_ip = result.stdout.strip()
        print(f"Deployment complete. The public IP of the VM is: {vm_public_ip}")    

    except subprocess.CalledProcessError as e:
        print(f"Error during Terraform apply: {e.stderr}")
        raise

##### SECTION 4: Main Workflow #####
def automate_deployment(input_text: str, repo_url: str):
    """
    Automate the entire deployment process.
    """
    # Step 1: Parse natural language input
    print("Parsing natural language input...")
    parsed_data = parse_with_gpt(input_text, model)

    if parsed_data == {"error": "Failed to parse GPT output."}:
        return
    else:
        print(f"Parsed data: {parsed_data}")

    # Step 2: Analyze the repository
    print("Analyzing repository...")
    local_dir = "repo"
    clone_or_open_repo(repo_url=repo_url, local_dir=local_dir)
    repo_analysis = detect_languages_and_frameworks(local_dir)
    print(f"Repository analysis: {repo_analysis}")

    # Step 3: Generate Terraform configuration
    print("Generating Terraform configuration...")
    generate_terraform_config(parsed_data, repo_analysis)

    # Step 4: Apply Terraform to deploy resources
    print("Deploying resources...")
    vm_public_ip = apply_terraform()

    # Provide the final output
    print(f"Deployment complete. Check the logs for more details.")

