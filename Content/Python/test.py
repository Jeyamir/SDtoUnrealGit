import subprocess

def generate_required_txt():
    # Run 'pip freeze' command and capture the output
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        # Write the output to required.txt
        with open('required.txt', 'w') as file:
            file.write(result.stdout)
        print("required.txt has been created successfully.")
    else:
        # If an error occurred, print the error
        print("Failed to generate required.txt:", result.stderr)

# Call the function
generate_required_txt()
