#!/usr/bin/env python
from json import load
from os.path import basename
from os.path import join

from numpy import savetxt

from control.plates.plate import Plate


def main(*argv):
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Translate a definition file and compute the plates.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Increase verbosity.')
    parser.add_argument('-s', '--source', required=True,
                        help='Source definition JSON file.')
    parser.add_argument('-o', '--output', required=True,
                        help='Output definition directory.')
    args = parser.parse_args(argv[1:])
    run(args.source, args.output, args.verbose)


def run(source, target, verbose=False):
    definitions = read_definition(source)
    for i, definition in enumerate(definitions):
        output_file = output_filename(source, target, i)
        if 'plate' not in definition:
            raise ValueError('Incorrect definition: no plate definition found.')
        write_plate(definition['plate'], output_file, verbose)
        definition['file'] = output_file
    write_definition(definitions, output_filename(source, target), verbose)


def write_definition(data, filename, verbose):
    if verbose:
        print('Writing definition file to "{f}".'.format(f=filename))
    with open(filename, 'w') as f:
        for d in data:
            f.write(', '.join(str(x) for x in
                [d['id'], d['plate']['dimension'], d['plate']['diameter']] +
                d['plate']['position'] + [d['sensor']['dimension'], d['sensor']['diameter']] +
                d['sensor']['position'] + [d['wavelength'], d['file']]
            ))


def construct_plate_definition(data):
    definition = {
        'dimension': data['dimension'],
        'diameter': data['diameter']
    }
    definition.update(data['definition'])
    return definition


def write_plate(data, filename, verbose=False):
    """Build a plate and write it to a csv.

    Args:
        data (dict): A dictionary containing the definition of the plate. It should
            have the following form:
                {
                    'dimension': <int>,
                    'diameter': <float>,
                    'definition': {
                        'type': <str>,
                        <additional keys>
                    },
                    [any additional keys]
                }
            While the outer dict may contain other keys, the 'definition' dict is
            required to contain all (and only) arguments the __init__ of the plate
            type accepts.
        filename (str): Name of the file to write the plate to.
        verbose (bool): If True, output (print) information. Defaults to False.
    """
    # Create the plate
    plate = Plate.create(construct_plate_definition(data))

    # Build the plate
    if verbose:
        print('Building plate: {p}.'.format(p=plate))
    result = plate.build()

    # Write the output
    if verbose:
        print('Writing plate to "{f}".'.format(f=filename))
    savetxt(filename, result, delimiter=',', fmt='%i')


def read_definition(source):
    with open(source, 'r') as f:
        return load(f)


def output_filename(source, target, plate=None):
    if source.lower().endswith('.json'):
        source = source[:-5]
    if plate is not None:
        return join(target, basename(source) + '_plate_{n}.csv'.format(n=plate))
    return join(target, basename(source) + '.csv')


if __name__ == '__main__':
    import sys
    main(*sys.argv)
