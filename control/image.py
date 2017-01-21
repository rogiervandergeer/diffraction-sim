from numpy import array, uint8, float_, complex_, zeros
from pandas import DataFrame, read_csv

COLUMNS = ['block_id', 'col_id', 'row_id', 'value']


def read_images(filename):
    df = read_csv(filename, names=('block_id', 'col_id', 'row_id', 'x', 'y'))
    if any(df['y']):
        df['value'] = df['value'] = df['x'].astype('complex') + complex(0, 1) * df['y'].astype('complex')
    else:
        df['value'] = df['x']
    return [
        Image.from_df(block_df, block_id=block_id)
        for block_id, block_df in df.groupby('block_id')
    ]


class Image:
    def __init__(self, rows, columns, block_id=None, dtype=float_):
        self.block_id = block_id
        self.data = zeros((rows, columns), dtype=dtype)

    def __repr__(self):
        return '{cls}({props})'.format(
            cls=self.__class__.__name__,
            props=', '.join(['{k}={v}'.format(k=key, v=repr(val)) for key, val
                             in (('rows', self.rows), ('columns', self.columns), ('block_id', self.block_id))
                             if val is not None])
        )

    @classmethod
    def from_df(cls, df, block_id=None):
        i = cls(0, 0, block_id=block_id)
        values = df.sort_values(['row_id', 'col_id']).value.values
        n_cols = df.col_id.max() + 1
        unpacked = [values[x:x + n_cols] for x in range(0, len(values), n_cols)]
        i.data = array(unpacked, dtype=df.value.dtype.type)
        return i

    def to_df(self):
        return DataFrame([
            {'row_id': row_id, 'col_id': col_id, 'value': self.data[row_id, col_id], 'block_id': self.block_id}
            for row_id in range(self.rows) for col_id in range(self.columns)
        ])


    @property
    def columns(self):
        return self.shape[1]

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def rows(self):
        return self.shape[0]

    @property
    def shape(self):
        return self.data.shape


