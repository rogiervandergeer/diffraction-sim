from subprocess import check_output


def build(optimisation=0):
    """Build the C code.

    Args:
        optimisation (int): Compiler optimisation flag. Can take any
          value between 0 and 3 inclusive. Defaults to 0.
    """
    check_output(['./build.sh', '-O{opt}'.format(opt=optimisation)])


def run(definition_file, id):
    pass

