from subprocess import check_output
from datetime import datetime
from os import mkdir
from os.path import isdir


def build(optimisation=0):
    """Build the C code.

    Args:
        optimisation (int): Compiler optimisation flag. Can take any
          value between 0 and 3 inclusive. Defaults to 0.
    """
    check_output(['./build.sh', '-O{opt}'.format(opt=optimisation)])


def create_folders():
    """Create the 'sources', 'plates' and 'output' folders."""
    for folder in ('sources/', 'plates/', 'output/'):
        if not isdir(folder):
            mkdir(folder)


def run(definition_file, output_file, definition_id=None):
    start = datetime.now()
    command = ['./bin/main.elf', definition_file, output_file]
    if type(definition_id) == int:
        command.append(str(definition_id))
    elif type(definition_id) == tuple:
        command.append(str(definition_id[0]))
        command.append(str(definition_id[1]))
    check_output(command)
    end = datetime.now()
    return (end-start).total_seconds()
