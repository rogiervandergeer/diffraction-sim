from json import load
from control.plates import Plate
from numpy import savetxt
from os.path import join, basename


def create_plates(definition_file,
                  source_directory='source/',
                  plate_directory='plates/',
                  verbose=False):
    name = basename(definition_file)[:-5] \
        if definition_file.endswith('.json') \
        else basename(definition_file)
    definitions = read_definitions(definition_file)
    for definition in definitions:
        filename = join(
            plate_directory,
            '{name}_{id}.csv'.format(name=name, id=definition.block_id)
        )
        definition.write_plate(filename)
    write_source(
        filename=join(source_directory, '{name}.csv'.format(name=name)),
        definitions=definitions,
        verbose=verbose
    )


def read_definitions(filename):
    with open(filename) as df:
        data = load(df)
    return [Definition(d) for d in data]


def write_source(filename, definitions, verbose=False):
    if verbose:
        print('Writing source file to "%s".' % filename)
    with open(filename, 'w') as sf:
        for definition in definitions:
            sf.write(definition.source)


class Definition:

    def __init__(self, data):
        self.data = data
        self.plate_file = None

    @property
    def block_id(self):
        return self.data['id']

    @property
    def plate(self):
        definition = {
            'dimension': self.data['plate']['dimension'],
            'diameter': self.data['plate']['diameter']
        }
        definition.update(self.data['plate']['definition'])
        return Plate.create(definition)

    @property
    def source(self):
        if not self.plate_file:
            raise RuntimeError('Cannot create definition source before writing plate.')
        values = [self.data['id']] \
            + [self.data['plate']['dimension'], self.data['plate']['diameter']] \
            + self.data['plate']['position'] \
            + [self.data['sensor']['dimension'] + self.data['sensor']['diameter']] \
            + self.data['sensor']['position'] \
            + [self.data['wavelength'], self.plate_file]
        return ', '.join(str(val) for val in values) + '\n'

    def write_plate(self, filename):
        plate = self.plate.build()
        savetxt(filename, plate, delimiter=',', fmt='%i')
        self.plate_file = filename
