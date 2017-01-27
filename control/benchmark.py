from json import dump, load


def read_benchmark():
    with open('benchmark.json') as bf:
        return load(bf)


def write_benchmark(data):
    with open('benchmark.json', 'w') as bf:
        dump(data, bf)
