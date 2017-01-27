#!/usr/bin/env python


def main(*argv):
    from argparse import ArgumentParser
    from control.definition import create_plates
    from control.utils import create_folders

    parser = ArgumentParser(description='Translate a definition file and compute the plates.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Increase verbosity.')
    parser.add_argument('-s', '--source', required=True,
                        help='Source definition JSON file.')
    parser.add_argument('-d', '--definitions', default='definitions/',
                        help='Output definition directory.')
    parser.add_argument('-p', '--plates', default='plates/',
                        help='Output plate directory.')
    args = parser.parse_args(argv[1:])
    create_folders()
    create_plates(args.source,
                  source_directory=args.source,
                  plate_directory=args.plates,
                  verbose=args.verbose)


if __name__ == '__main__':
    import sys
    main(*sys.argv)
