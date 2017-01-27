from json import dump, load
from control.utils import run, build


def read_benchmark():
    with open('benchmark.json') as bf:
        return load(bf)


def write_benchmark(data):
    with open('benchmark.json', 'w') as bf:
        dump(data, bf)


def benchmark(benchmark_id, optimisation):
    build(optimisation=optimisation)
    return run('plates/benchmark.csv', 'output/benchmark.csv', definition_id=benchmark_id)
