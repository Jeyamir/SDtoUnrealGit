import unreal
import subprocess
from pathlib import Path
import os
import sys 

PYTHON_INTERPRETER_PATH = unreal.get_interpreter_executable_path()
assert Path(PYTHON_INTERPRETER_PATH).exists(), f"Python not found at '{PYTHON_INTERPRETER_PATH}'"
sitepackages = Path(PYTHON_INTERPRETER_PATH).parent / "Lib" / "site-packages"
sys.path.append(str(sitepackages))
import pkg_resources
import threading

def check_installed_packages():
    """Create a set of already installed packages."""
    return {pkg.key for pkg in pkg_resources.working_set}

def install_packages_from_requirements(requirements_file):
    """Install packages specified in the given requirements.txt file only if not already installed."""
    installed_packages = check_installed_packages()
    with open(requirements_file, 'r') as file:
        required_packages = [line.strip().split('==')[0] for line in file if line.strip() and not line.startswith('#')]
    
    packages_to_install = [pkg for pkg in required_packages if pkg.lower() not in installed_packages]
    if packages_to_install:
        command = [PYTHON_INTERPRETER_PATH, '-m', 'pip', 'install', '--no-deps'] + packages_to_install
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            unreal.log("All packages installed successfully.")
            unreal.log(result.stdout)
        else:
            unreal.log_warning(result.stderr)
            unreal.log_warning("Failed to install packages.")
    else:
        unreal.log("All required packages are already installed.")


def pip_install_async(requirements_path):
    thread = threading.Thread(target=install_packages_from_requirements, args=(str(requirements_path),))
    thread.start()

requirements_path = Path(__file__).parent / "requirements.txt"
print(requirements_path)

# Use pip_install_async instead of pip_instal
unreal.EditorDialog.show_message("Module Install Notice", "Pip is installing the required packages for Stable Diffusion Window.\n This may take some time.", unreal.AppMsgType.OK)
# install_packages_from_requirements(requirements_path)
pip_install_async(requirements_path)
# pip_install(missing)
print(PYTHON_INTERPRETER_PATH)