# import all functions
from Functions import *


# requests User Input and stores it
print("Please enter your github url or provide the path to the zip-file:")
github = input()

print("Please enter your request:")
request = input()

# prints message
print("Processing Request...")

automate_deployment(request, github)

# https://github.com/Arvo-AI/hello_world.git