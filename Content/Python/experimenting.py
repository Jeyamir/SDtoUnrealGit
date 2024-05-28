import unreal
import subprocess
from pathlib import Path
import os
import sys
from installPackages import install, run_accelerate_config

PYTHON_INTERPRETER_PATH = unreal.get_interpreter_executable_path()
assert Path(PYTHON_INTERPRETER_PATH).exists(), f"Python not found at '{PYTHON_INTERPRETER_PATH}'"

parent_dir = unreal.Paths.project_intermediate_dir()
sitepackages = os.path.join(parent_dir, "PipInstall", "Lib", "site-packages")
sys.path.append(sitepackages)
print(f"Added to sys.path: {sitepackages}")

# Construct the path to accelerate-config executable
accelerate_config = os.path.join(sitepackages, 'bin', 'accelerate-config.exe')

# Verify that the executable exists
if not os.path.isfile(accelerate_config):
    raise FileNotFoundError(f"Executable not found: {accelerate_config}")

# Set the PYTHONPATH environment variable to include site-packages
env = os.environ.copy()
env['PYTHONPATH'] = sitepackages + os.pathsep + env.get('PYTHONPATH', '')

# Run the accelerate-config command using the specified Python executable
result = subprocess.run([PYTHON_INTERPRETER_PATH, accelerate_config, 'default'], capture_output=True, text=True, env=env)

# Print the result
print("stdout:", result.stdout)
print("stderr:", result.stderr)
print("returncode:", result.returncode)
