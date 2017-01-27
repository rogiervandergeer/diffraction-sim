#!/usr/bin/env python


def main(*argv):
    from argparse import ArgumentParser
    from control.definition import create_plates, read_definitions
    from control.utils import create_folders
    from control.benchmark import benchmark

    parser = ArgumentParser(description='Translate a definition file and compute the plates.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Increase verbosity.')
    args = parser.parse_args(argv[1:])

    create_folders()
    create_plates(source_file='sources/benchmark.json')
    for definition in read_definitions('sources/benchmark.json'):
        for opt in range(4):
            s = benchmark(definition.block_id, opt)
            print(s)


if __name__ == '__main__':
    import sys
    main(*sys.argv)
