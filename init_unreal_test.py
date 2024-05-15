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
def pip_install(packages):
    # dont show window
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    proc = subprocess.Popen(
        [
            PYTHON_INTERPRETER_PATH, 
            '-m', 'pip', 'install',  '--no-warn-script-location', "--no-cache-dir",
            *packages
        ],
        startupinfo = info,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        encoding = "utf-8"
    )

    while proc.poll() is None:
        unreal.log(proc.stdout.readline().strip())
        unreal.log_warning(proc.stderr.readline().strip())

    return proc.poll()
def Menu():
    menus = unreal.ToolMenus.get()

    # __file__ gives the path of the current file; os.path.abspath ensures it's absolute.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_file_path = os.path.join(current_dir, "QtWindow.py")

    # # os.path.dirname gets the directory containing the file.
    # current_dir = os.path.dirname(current_file_path)

    # Find the 'Main' menu, this should not fail,
    # but if we're looking for a menu we're unsure about 'if not'
    # works as nullptr check,
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if not main_menu:
        print("Failed to find the 'Main' menu. Something is wrong in the force!")

    entry = unreal.ToolMenuEntry(
                                name="Python.Tools",
                                # If you pass a type that is not supported Unreal will let you know,
                                type=unreal.MultiBlockType.MENU_ENTRY,
                                # this will tell unreal to insert this entry into the First spot of the menu
                                insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
    )
    entry.set_label("Open Stable Diffusion")
    # this is what gets executed on click

    #run the pyside file
    command_to_run = main_file_path.replace('\\', '/')
    entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, custom_type='ExecuteFile', string=command_to_run)
    

    # add a new menu called PyTools to the MainMenu bar. You should probably rename the last 3 properties here to useful things for you
    script_menu = main_menu.add_sub_menu(main_menu.get_name(), "StableDiffusionTool", "StableDiffusionTool", "StableDiffusionTool")
    # add our new entry to the new youe
    script_menu.add_menu_entry("Scripts",entry)
    # refresh the UI
    menus.refresh_all_widgets()

# Put here your required python packages
required = {'Pyside6', 'torch', 'diffusers', 'pillow', 'transformers', 'numpy', 'torchvision', 'torchaudio', 'opencv-python', 'compel', 'onnxruntime', 'accelerate'}


append_path()
Menu()

import threading

def pip_install_async(packages):
    def install():
        # your existing pip_install function code here
        # remember to remove or modify any Unreal logging functions if they are not thread-safe
        pip_install(packages)
    
    # Start the installation in a new thread
    thread = threading.Thread(target=install)
    thread.start()

# Use pip_install_async instead of pip_instal
unreal.EditorDialog.show_message("Module Install Notice", "Pip is installing the required packages for Stable Diffusion Window.\n This may take some time.", unreal.AppMsgType.OK)
pip_install_async(required)
print(required)
