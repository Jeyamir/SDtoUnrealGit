import unreal
import subprocess
from pathlib import Path
import os
import sys 

PYTHON_INTERPRETER_PATH = unreal.get_interpreter_executable_path()
assert Path(PYTHON_INTERPRETER_PATH).exists(), f"Python not found at '{PYTHON_INTERPRETER_PATH}'"
file_path = Path(PYTHON_INTERPRETER_PATH)
parent_dir = file_path.parent
sitepackages = os.path.join(parent_dir, "Lib")
sitepackages = os.path.join(sitepackages, "site-packages")
sys.path.append(sitepackages)

def append_path():
    if str(sitepackages) not in sys.path:
        sys.path.append(str(sitepackages))
    sys.path = [p for p in sys.path if p is not None]
    
import pkg_resources
def install_packages_from_requirements(requirements_file):
    """Install packages specified in the given requirements.txt file."""
    try:
        # Construct the command to execute
        command = [PYTHON_INTERPRETER_PATH, '-m', 'pip', 'install', '-r', requirements_file, '--no-warn-script-location', "--no-cache-dir"]
        # command = [PYTHON_INTERPRETER_PATH, '-m', 'pip', 'debug', '-vvv']
        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the installation was successful
        if result.returncode == 0:
            print("All packages installed successfully.")
            print(result.stdout)
        else:
            print(result.stderr)
            print("Failed to install packages.")
        unreal.log(result.stdout)
        unreal.log_warning(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages from {requirements_file}. Error: {e}")


# Path to your requirements.txt file
current_file_path = Path(__file__)
current_file_dir = current_file_path.parent
requirements_path = current_file_dir / "requirements.txt"
print(requirements_path)
# Install packages

# append_path()

import threading

def pip_install_async(packages):
    def install():
        # your existing pip_install function code here
        # remember to remove or modify any Unreal logging functions if they are not thread-safe
        install_packages_from_requirements(packages)
    
    # Start the installation in a new thread
    thread = threading.Thread(target=install)
    thread.start()


# Use pip_install_async instead of pip_instal
unreal.EditorDialog.show_message("Module Install Notice", "Pip is installing the required packages for Stable Diffusion Window.\n This may take some time.", unreal.AppMsgType.OK)
# install_packages_from_requirements(requirements_path)
pip_install_async(requirements_path)
# pip_install(missing)
print(PYTHON_INTERPRETER_PATH)