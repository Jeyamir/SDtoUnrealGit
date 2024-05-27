import unreal
from pathlib import Path
import subprocess
import threading
import sys
import tempfile

PYTHON_INTERPRETER_PATH = unreal.get_interpreter_executable_path()
assert Path(PYTHON_INTERPRETER_PATH).exists(), f"Python not found at '{PYTHON_INTERPRETER_PATH}'"
sitepackages = Path(PYTHON_INTERPRETER_PATH).parent / "Lib" / "site-packages"
sys.path.append(str(sitepackages))
import pkg_resources


def check_installed_packages():
    """Create a set of already installed packages."""
    return {pkg.key for pkg in pkg_resources.working_set}

def install_packages_from_requirements(requirements_file, target_directory):
    """Install packages specified in the given requirements.txt file to a defined target directory."""
    installed_packages = check_installed_packages()
    
    # Read the requirements file and filter out comments and empty lines
    with open(requirements_file, 'r') as file:
        lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    
    # Separate index-url lines and package lines
    index_urls = [line for line in lines if line.startswith('--index-url')]
    packages = [line for line in lines if not line.startswith('--index-url')]
    
    # Check which packages are not already installed
    packages_to_install = [pkg for pkg in packages if pkg.lower().split('==')[0] not in installed_packages]
    
    if packages_to_install:
        print(packages_to_install)
        # Create a temporary requirements file including index-url
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_req_file:
            temp_req_file.write('\n'.join(index_urls + packages_to_install))
            temp_req_file_path = temp_req_file.name
        
        # Build the pip install command
        command = [
            PYTHON_INTERPRETER_PATH, '-m', 'pip', 'install', '--no-deps',
            '--target', str(target_directory), '-r', temp_req_file_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            unreal.log("All packages installed successfully.")
            unreal.log(result.stdout)
        else:
            unreal.log_warning(result.stderr)
            unreal.log_warning("Failed to install packages.")
        
        # Clean up the temporary requirements file
        Path(temp_req_file_path).unlink()
    else:
        unreal.log("All required packages are already installed.")

def pip_install_async(requirements_path, target_directory):
    thread = threading.Thread(target=install_packages_from_requirements, args=(str(requirements_path), target_directory))
    thread.start()


requirements_path = Path(__file__).parent / "requirements.txt"
intermediate_path_str = unreal.Paths.project_intermediate_dir()
target_directory = Path(intermediate_path_str) / "PipInstall" / "Lib" / "site-packages"
unreal.EditorDialog.show_message("Module Install Notice", "Pip is installing the required packages for Stable Diffusion Window.\n This may take some time.", unreal.AppMsgType.OK)
pip_install_async(requirements_path, target_directory)
print(str(target_directory))
