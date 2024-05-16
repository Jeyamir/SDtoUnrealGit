import subprocess

def generate_requirements():
    # Define the path to the virtual environment's pip executable
    
    # Define the output file for the requirements
    output_file = 'requiresd.txt'

    # Execute pip freeze and write the output to the file
    with open(output_file, 'w') as f:
        subprocess.run(['pip', 'freeze', '>', 'requiresd.txt'], stdout=f)

    print(f'Requirements file generated at {output_file}')

if __name__ == "__main__":
    generate_requirements()
