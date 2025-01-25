## NPL Inits ##
import openai
import os
from dotenv import load_dotenv

## Github Analysis ##
from git import Repo
import zipfile
import shutil
from collections import Counter
from pathlib import Path

## Terraform Subprocess ##
import subprocess
import subprocess



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


# Function to apply Terraform configuration
def apply_terraform(terraform_vars: Dict[str, Any]):
    """
    Apply the generated Terraform configuration.
    """
    # Initialize Terraform
    subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR)

    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR)

    # Optionally, output the public IP or other details after deployment
    print("VM Deployed Successfully. Logs will be available in Terraform output.")


# Function to replace localhost with VM's public IP in the app
def update_app_config(repo_dir: str, vm_ip: str):
    """
    Update the application code to replace 'localhost' with the deployed VM's public IP.
    """
    app_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir)]
    
    for file in app_files:
        with open(file, 'r') as f:
            file_content = f.read()

        file_content = file_content.replace('localhost', vm_ip)

        with open(file, 'w') as f:
            f.write(file_content)


# Main function to automate the deployment process
def automate_deployment(nl_input: str, repo_url: str):
    """
    Automate the full deployment process based on the natural language input and repository.
    """
    # Step 1: Parse natural language input
    deployment_details = parse_natural_language(nl_input)

    # Step 2: Download and analyze the repository
    repo_dir = download_repository(repo_url)
    repo_analysis = analyze_repository(repo_dir)

    # Step 3: Generate Terraform configuration for GCP
    terraform_vars = generate_terraform_config_gcp(deployment_details["app_type"], repo_dir)

    # Step 4: Apply Terraform configuration to provision the VM
    apply_terraform(terraform_vars)

    # Step 5: Update app configuration to replace localhost with the public IP of the deployed VM
    # Here, you'd get the public IP of the deployed VM (for simplicity, we're hardcoding it for now)
    vm_ip = "XX.XX.XX.XX"  # Replace this with actual VM IP
    update_app_config(repo_dir, vm_ip)

    print(f"Deployment Successful: Your app is accessible at http://{vm_ip}")

if __name__ == "__main__":
    # Example usage
    nl_input = "Deploy this Flask application on GCP"
    repo_url = "https://github.com/Arvo-AI/hello_world"
    automate_deployment(nl_input, repo_url)
# Function to apply Terraform configuration
def apply_terraform(terraform_vars: Dict[str, Any]):
    """
    Apply the generated Terraform configuration.
    """
    # Initialize Terraform
    subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR)

    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR)

    # Optionally, output the public IP or other details after deployment
    print("VM Deployed Successfully. Logs will be available in Terraform output.")


# Function to replace localhost with VM's public IP in the app
def update_app_config(repo_dir: str, vm_ip: str):
    """
    Update the application code to replace 'localhost' with the deployed VM's public IP.
    """
    app_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir)]
    
    for file in app_files:
        with open(file, 'r') as f:
            file_content = f.read()

        file_content = file_content.replace('localhost', vm_ip)

        with open(file, 'w') as f:
            f.write(file_content)


# Main function to automate the deployment process
def automate_deployment(nl_input: str, repo_url: str):
    """
    Automate the full deployment process based on the natural language input and repository.
    """
    # Step 1: Parse natural language input
    deployment_details = parse_natural_language(nl_input)

    # Step 2: Download and analyze the repository
    repo_dir = download_repository(repo_url)
    repo_analysis = analyze_repository(repo_dir)

    # Step 3: Generate Terraform configuration for GCP
    terraform_vars = generate_terraform_config_gcp(deployment_details["app_type"], repo_dir)

    # Step 4: Apply Terraform configuration to provision the VM
    apply_terraform(terraform_vars)

    # Step 5: Update app configuration to replace localhost with the public IP of the deployed VM
    # Here, you'd get the public IP of the deployed VM (for simplicity, we're hardcoding it for now)
    vm_ip = "XX.XX.XX.XX"  # Replace this with actual VM IP
    update_app_config(repo_dir, vm_ip)

    print(f"Deployment Successful: Your app is accessible at http://{vm_ip}")

if __name__ == "__main__":
    # Example usage
    nl_input = "Deploy this Flask application on GCP"
    repo_url = "https://github.com/Arvo-AI/hello_world"
    automate_deployment(nl_input, repo_url)
# Function to apply Terraform configuration
def apply_terraform(terraform_vars: Dict[str, Any]):
    """
    Apply the generated Terraform configuration.
    """
    # Initialize Terraform
    subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR)

    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR)

    # Optionally, output the public IP or other details after deployment
    print("VM Deployed Successfully. Logs will be available in Terraform output.")


# Function to replace localhost with VM's public IP in the app
def update_app_config(repo_dir: str, vm_ip: str):
    """
    Update the application code to replace 'localhost' with the deployed VM's public IP.
    """
    app_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir)]
    
    for file in app_files:
        with open(file, 'r') as f:
            file_content = f.read()

        file_content = file_content.replace('localhost', vm_ip)

        with open(file, 'w') as f:
            f.write(file_content)


# Main function to automate the deployment process
def automate_deployment(nl_input: str, repo_url: str):
    """
    Automate the full deployment process based on the natural language input and repository.
    """
    # Step 1: Parse natural language input
    deployment_details = parse_natural_language(nl_input)

    # Step 2: Download and analyze the repository
    repo_dir = download_repository(repo_url)
    repo_analysis = analyze_repository(repo_dir)

    # Step 3: Generate Terraform configuration for GCP
    terraform_vars = generate_terraform_config_gcp(deployment_details["app_type"], repo_dir)

    # Step 4: Apply Terraform configuration to provision the VM
    apply_terraform(terraform_vars)

    # Step 5: Update app configuration to replace localhost with the public IP of the deployed VM
    # Here, you'd get the public IP of the deployed VM (for simplicity, we're hardcoding it for now)
    vm_ip = "XX.XX.XX.XX"  # Replace this with actual VM IP
    update_app_config(repo_dir, vm_ip)

    print(f"Deployment Successful: Your app is accessible at http://{vm_ip}")


if __name__ == "__main__":
    # Example usage
    nl_input = "Deploy this Flask application on GCP"
    repo_url = "https://github.com/Arvo-AI/hello_world"
    automate_deployment(nl_input, repo_url)##### TERRAFORM #####

# Function to apply Terraform configuration
def apply_terraform(terraform_vars: Dict[str, Any]):
    """
    Apply the generated Terraform configuration.
    """
    # Initialize Terraform
    subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR)

    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR)

    # Optionally, output the public IP or other details after deployment
    print("VM Deployed Successfully. Logs will be available in Terraform output.")


# Function to replace localhost with VM's public IP in the app
def update_app_config(repo_dir: str, vm_ip: str):
    """
    Update the application code to replace 'localhost' with the deployed VM's public IP.
    """
    app_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir)]
    
    for file in app_files:
        with open(file, 'r') as f:
            file_content = f.read()

        file_content = file_content.replace('localhost', vm_ip)

        with open(file, 'w') as f:
            f.write(file_content)


# Main function to automate the deployment process
def automate_deployment(nl_input: str, repo_url: str):
    """
    Automate the full deployment process based on the natural language input and repository.
    """
    # Step 1: Parse natural language input
    deployment_details = parse_natural_language(nl_input)

    # Step 2: Download and analyze the repository
    repo_dir = download_repository(repo_url)
    repo_analysis = analyze_repository(repo_dir)

    # Step 3: Generate Terraform configuration for GCP
    terraform_vars = generate_terraform_config_gcp(deployment_details["app_type"], repo_dir)

    # Step 4: Apply Terraform configuration to provision the VM
    apply_terraform(terraform_vars)

    # Step 5: Update app configuration to replace localhost with the public IP of the deployed VM
    # Here, you'd get the public IP of the deployed VM (for simplicity, we're hardcoding it for now)
    vm_ip = "XX.XX.XX.XX"  # Replace this with actual VM IP
    update_app_config(repo_dir, vm_ip)

    print(f"Deployment Successful: Your app is accessible at http://{vm_ip}")


if __name__ == "__main__":
    # Example usage
    nl_input = "Deploy this Flask application on GCP"
    repo_url = "https://github.com/Arvo-AI/hello_world"
    automate_deployment(nl_input, repo_url)
# Function to apply Terraform configuration
def apply_terraform(terraform_vars: Dict[str, Any]):
    """
    Apply the generated Terraform configuration.
    """
    # Initialize Terraform
    subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR)

    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR)

    # Optionally, output the public IP or other details after deployment
    print("VM Deployed Successfully. Logs will be available in Terraform output.")


# Function to replace localhost with VM's public IP in the app
def update_app_config(repo_dir: str, vm_ip: str):
    """
    Update the application code to replace 'localhost' with the deployed VM's public IP.
    """
    app_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir)]
    
    for file in app_files:
        with open(file, 'r') as f:
            file_content = f.read()

        file_content = file_content.replace('localhost', vm_ip)

        with open(file, 'w') as f:
            f.write(file_content)


# Main function to automate the deployment process
def automate_deployment(nl_input: str, repo_url: str):
    """
    Automate the full deployment process based on the natural language input and repository.
    """
    # Step 1: Parse natural language input
    deployment_details = parse_natural_language(nl_input)

    # Step 2: Download and analyze the repository
    repo_dir = download_repository(repo_url)
    repo_analysis = analyze_repository(repo_dir)

    # Step 3: Generate Terraform configuration for GCP
    terraform_vars = generate_terraform_config_gcp(deployment_details["app_type"], repo_dir)

    # Step 4: Apply Terraform configuration to provision the VM
    apply_terraform(terraform_vars)

    # Step 5: Update app configuration to replace localhost with the public IP of the deployed VM
    # Here, you'd get the public IP of the deployed VM (for simplicity, we're hardcoding it for now)
    vm_ip = "XX.XX.XX.XX"  # Replace this with actual VM IP
    update_app_config(repo_dir, vm_ip)

    print(f"Deployment Successful: Your app is accessible at http://{vm_ip}")


if __name__ == "__main__":
    # Example usage
    nl_input = "Deploy this Flask application on GCP"
    repo_url = "https://github.com/Arvo-AI/hello_world"
    automate_deployment(nl_input, repo_url)
# Function to apply Terraform configuration
def apply_terraform(terraform_vars: Dict[str, Any]):
    """
    Apply the generated Terraform configuration.
    """
    # Initialize Terraform
    subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR)

    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR)

    # Optionally, output the public IP or other details after deployment
    print("VM Deployed Successfully. Logs will be available in Terraform output.")


# Function to replace localhost with VM's public IP in the app
def update_app_config(repo_dir: str, vm_ip: str):
    """
    Update the application code to replace 'localhost' with the deployed VM's public IP.
    """
    app_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir)]
    
    for file in app_files:
        with open(file, 'r') as f:
            file_content = f.read()

        file_content = file_content.replace('localhost', vm_ip)

        with open(file, 'w') as f:
            f.write(file_content)


# Main function to automate the deployment process
def automate_deployment(nl_input: str, repo_url: str):
    """
    Automate the full deployment process based on the natural language input and repository.
    """
    # Step 1: Parse natural language input
    deployment_details = parse_natural_language(nl_input)

    # Step 2: Download and analyze the repository
    repo_dir = download_repository(repo_url)
    repo_analysis = analyze_repository(repo_dir)

    # Step 3: Generate Terraform configuration for GCP
    terraform_vars = generate_terraform_config_gcp(deployment_details["app_type"], repo_dir)

    # Step 4: Apply Terraform configuration to provision the VM
    apply_terraform(terraform_vars)

    # Step 5: Update app configuration to replace localhost with the public IP of the deployed VM
    # Here, you'd get the public IP of the deployed VM (for simplicity, we're hardcoding it for now)
    vm_ip = "XX.XX.XX.XX"  # Replace this with actual VM IP
    update_app_config(repo_dir, vm_ip)

    print(f"Deployment Successful: Your app is accessible at http://{vm_ip}")


if __name__ == "__main__":
    # Example usage
    nl_input = "Deploy this Flask application on GCP"
    repo_url = "https://github.com/Arvo-AI/hello_world"
    automate_deployment(nl_input, repo_url)# Function to generate Terraform configuration dynamically for GCP
def generate_terraform_config_gcp(app_type: str, repo_dir: str):
    terraform_vars = {
        "machine_type": "e2-micro",  # Default size for GCP, can be adjusted based on the app_type
        "os_image_family": "debian-11",  # Default OS image family
        "disk_size": "20",  # Disk size in GB
    }

    # Modify configuration based on app type
    if app_type == "Node.js":
        terraform_vars["machine_type"] = "e2-medium"
    elif app_type == "Python (Flask/Django)":
        terraform_vars["machine_type"] = "e2-standard-2"
    elif app_type == "Java":
        terraform_vars["machine_type"] = "e2-standard-4"

    # Create Terraform configuration
    terraform_config = f"""
    provider "google" {{
        credentials = file("<PATH_TO_YOUR_SERVICE_ACCOUNT_KEY>.json")
        project     = "<YOUR_GCP_PROJECT_ID>"
        region      = "us-central1"
    }}

    resource "google_compute_instance" "app_vm" {{
        name         = "app-vm"
        machine_type = "{terraform_vars['machine_type']}"
        zone         = "us-central1-a"

        boot_disk {{
            initialize_params {{
                image = "projects/debian-cloud/global/images/family/{terraform_vars['os_image_family']}"
                size  = {terraform_vars['disk_size']}
            }}
        }}

        network_interface {{
            network = "default"
            access_config {{
            }}
        }}

        tags = ["http-server"]

        metadata_startup_script = <<EOT
        #!/bin/bash
        sudo apt update
        sudo apt install -y python3 python3-pip
        cd /home
        git clone {repo_dir}
        cd repo
        pip3 install -r requirements.txt
        python3 app.py
        EOT
    }}
    """

    # Save the Terraform configuration to a file
    os.makedirs(TERRAFORM_DIR, exist_ok=True)
    with open(os.path.join(TERRAFORM_DIR, 'main.tf'), 'w') as tf_file:
        tf_file.write(terraform_config)

    return terraform_vars


# Function to apply Terraform configuration
def apply_terraform(terraform_vars: Dict[str, Any]):
    """
    Apply the generated Terraform configuration.
    """
    # Initialize Terraform
    subprocess.run(["terraform", "init"], cwd=TERRAFORM_DIR)

    # Apply Terraform configuration
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_DIR)

    # Optionally, output the public IP or other details after deployment
    print("VM Deployed Successfully. Logs will be available in Terraform output.")


# Function to replace localhost with VM's public IP in the app
def update_app_config(repo_dir: str, vm_ip: str):
    """
    Update the application code to replace 'localhost' with the deployed VM's public IP.
    """
    app_files = [os.path.join(repo_dir, file) for file in os.listdir(repo_dir)]
    
    for file in app_files:
        with open(file, 'r') as f:
            file_content = f.read()

        file_content = file_content.replace('localhost', vm_ip)

        with open(file, 'w') as f:
            f.write(file_content)


# Main function to automate the deployment process
def automate_deployment(nl_input: str, repo_url: str):
    """
    Generate Terraform configuration for GCP based on app type.
    """
    terraform_vars = {
        "machine_type": "e2-micro",  # Default size for GCP, can be adjusted based on the app_type
        "os_image_family": "debian-11",  # Default OS image family
        "disk_size": "20",  # Disk size in GB
    }

    # Modify configuration based on app type
    if app_type == "Node.js":
        terraform_vars["machine_type"] = "e2-medium"
    elif app_type == "Python (Flask/Django)":
        terraform_vars["machine_type"] = "e2-standard-2"
    elif app_type == "Java":
        terraform_vars["machine_type"] = "e2-standard-4"
