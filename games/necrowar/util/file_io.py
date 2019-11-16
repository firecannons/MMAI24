import os

def get_script_path(script):
    return os.path.dirname(os.path.realpath(script))

def get_path(script, file):
    return os.path.join(get_script_path(script), file)
