import unreal
from pathlib import Path
import subprocess
import sys
import os
PYTHON_INTERPRETER_PATH = unreal.get_interpreter_executable_path()
assert Path(PYTHON_INTERPRETER_PATH).exists(), f"Python not found at '{PYTHON_INTERPRETER_PATH}'"
sitepackages = Path(PYTHON_INTERPRETER_PATH).parent / "Lib" / "site-packages"
sys.path.append(str(sitepackages))

def uninstall_package_from_directory(package_name, target_directory):
    # Define the command to uninstall the package
    command = [sys.executable, '-m', 'pip', 'uninstall', '--target', str(target_directory), '-y', package_name]

    # Set the PYTHONPATH environment variable to include the target directory
    env = os.environ.copy()
    env['PYTHONPATH'] = str(target_directory)

    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            print(f"Successfully uninstalled {package_name} from {target_directory}")
        else:
            print(f"Error occurred while uninstalling {package_name}: {result.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    package_to_uninstall = "xformers"
    # Replace with the actual package name
    intermediate_path_str = unreal.Paths.project_intermediate_dir()
    target_directory = Path(intermediate_path_str) / "PipInstall" / "Lib" / "site-packages"
    target_directory = str(target_directory)  # Replace with the path to your target directory
    uninstall_package_from_directory(package_to_uninstall, target_directory)
