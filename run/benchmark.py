#!/usr/bin/env python


def main(*argv):
    from argparse import ArgumentParser
    from json import load, dump
    from control.definition import create_plates, read_definitions
    from control.image import compare_images
    from control.utils import create_folders
    from control.benchmark import benchmark

    parser = ArgumentParser(description='Translate a definition file and compute the plates.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Increase verbosity.')
    parser.add_argument('-t', '--tolerance', action='store', default=1e-4,
                        help='Image comparison tolerance.', metavar='TOL')
    parser.add_argument('-s', '--store-performance', action='store_true', default=False,
                        help='Overwrite the performance reference file.', dest='store')
    args = parser.parse_args(argv[1:])

    with open('reference/performance.json') as rf:
        performance_data = load(rf)
    current_performance = {}

    create_folders()
    create_plates(source_file='sources/benchmark.json')
    for definition in read_definitions('sources/benchmark.json'):
        current_performance[definition.block_id] = {}
        print(' == Definition %s' % definition.block_id)
        for opt in range(4):
            seconds = benchmark(definition.block_id, opt)
            cycle_time = seconds / definition.iterations
            current_performance[definition.block_id][opt] = cycle_time
            reference_time = lookup_performance(performance_data, definition.block_id, opt)
            print(' O{n}: {s:1.3g} seconds, {c:1.4g} ({r:1.4g}) seconds per cycle (reference).'.format(
                n=opt, s=seconds, c=cycle_time, r=reference_time if reference_time else 0
            ))

            diffs = compare_images(
                reference_file='reference/benchmark{i}.csv'.format(i=definition.block_id),
                comparison_file='output/benchmark.csv', tolerance=args.tolerance,
                check_ids=False
            )
            print('Difference: %1.2g' % diffs[0])
    if args.store:
        with open('reference/performance.json', 'w') as rf:
            dump(current_performance, rf)


def lookup_performance(d, block_id, opt):
    try:
        return d[str(block_id)][str(opt)]
    except KeyError:
        return None


if __name__ == '__main__':
    import sys
    main(*sys.argv)
