import unreal
from pathlib import Path
import subprocess
import threading
import sys
import tempfile
import os
PYTHON_INTERPRETER_PATH = unreal.get_interpreter_executable_path()
assert Path(PYTHON_INTERPRETER_PATH).exists(), f"Python not found at '{PYTHON_INTERPRETER_PATH}'"
sitepackages = Path(PYTHON_INTERPRETER_PATH).parent / "Lib" / "site-packages"

sys.path.append(str(sitepackages))
sitepackages = os.path.join(unreal.Paths.project_intermediate_dir(), "PipInstall", "Lib", "site-packages")

sys.path.append(str(sitepackages))
import pkg_resources

def add_to_path(new_path):
    # Get the current PATH environment variable
    current_path = os.environ.get('PATH', '')

    # Check if the new path is already in the PATH
    if new_path not in current_path.split(os.pathsep):
        # Add the new path to the PATH
        new_path = os.path.abspath(new_path)
        os.environ['PATH'] = new_path + os.pathsep + current_path

        # Persist the change to the PATH environment variable
        if sys.platform == 'win32':
            # On Windows, update the registry to make the change permanent
            import winreg as reg
            reg_key = reg.OpenKey(reg.HKEY_CURRENT_USER, 'Environment', 0, reg.KEY_ALL_ACCESS)
            reg.SetValueEx(reg_key, 'PATH', 0, reg.REG_EXPAND_SZ, os.environ['PATH'])
            reg.CloseKey(reg_key)
        else:
            # On Unix-like systems, update the shell profile
            profile_path = os.path.expanduser('~/.bashrc')  # or ~/.bash_profile, ~/.zshrc, etc.
            with open(profile_path, 'a') as profile_file:
                profile_file.write(f'\nexport PATH="{new_path}:{current_path}"\n')
    else:
        print(f'{new_path} is already in the PATH')

def check_installed_packages():
    """Create a set of already installed packages."""
    return {pkg.key for pkg in pkg_resources.working_set}

def run_accelerate_config():
    """Run the accelerate configuration command."""

    # Get the project intermediate directory
    acceleratePath = os.path.join(unreal.Paths.project_intermediate_dir(), "PipInstall", "Lib", "site-packages")
    # Add the bin directory to the system PATH
    bin_path = os.path.join(acceleratePath, "bin")
    add_to_path(bin_path)
    print(f"Added to system PATH: {bin_path}")

    try:
        command = ['accelerate', 'config', 'default']
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            unreal.log("Accelerate configuration completed successfully.")
            unreal.log(result.stdout)
        else:
            unreal.log_warning(result.stderr)
            unreal.log_warning("Failed to configure accelerate.")
    except subprocess.CalledProcessError as e:
        unreal.log_warning(f"Error occurred: {e}")
        unreal.log_warning(f"Command output: {e.output}")
        unreal.log_warning(f"Command errors: {e.stderr}")

# def run_accelerate_config():
#     """Run the accelerate configuration command."""
#     try:
#         # Import the accelerate module dynamically
#         import importlib.util
#         spec = importlib.util.spec_from_file_location("accelerate", str(Path(unreal.Paths.project_intermediate_dir()) / "PipInstall" / "Lib" / "site-packages" / "accelerate" / "__init__.py"))
#         accelerate = importlib.util.module_from_spec(spec)
#         sys.modules["accelerate"] = accelerate
#         spec.loader.exec_module(accelerate)

#         # Run the accelerate configuration
#         accelerate_config = accelerate.commands.config.default.main
#         accelerate_config()

#         unreal.log("Accelerate configuration completed successfully.")
#     except Exception as e:
#         unreal.log_warning(f"Error occurred: {e}")

class ThreadWithCallback(threading.Thread):
    def __init__(self, target, callback, args=()):
        super().__init__()
        self._target = target
        self._args = args
        self.callback = callback

    def run(self):
        try:
            if self._target:
                self._target(*self._args)
        finally:
            if self.callback:
                self.callback()

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
    thread = ThreadWithCallback(
        target=install_packages_from_requirements,
        callback=run_accelerate_config,
        args=(str(requirements_path), target_directory)
    )
    thread.start()

def install():
    requirements_path = Path(__file__).parent / "requirements.txt"
    intermediate_path_str = unreal.Paths.project_intermediate_dir()
    target_directory = Path(intermediate_path_str) / "PipInstall" / "Lib" / "site-packages"
    unreal.EditorDialog.show_message("Module Install Notice", "Pip is installing the required packages for Stable Diffusion Window.\n This may take some time.", unreal.AppMsgType.OK)
    pip_install_async(requirements_path, target_directory)
    requirements_path = Path(__file__).parent / "xformers.txt"
    pip_install_async(requirements_path, target_directory)

