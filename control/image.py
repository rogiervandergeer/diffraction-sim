from numpy import array, uint8, float_, complex_, zeros
from pandas import DataFrame, read_csv

COLUMNS = ['block_id', 'col_id', 'row_id', 'value']


def read_images(filename):
    """Read images from a file.

    This file is expected to be formatted as csv with four or five columns:
    - block_id, the id of the image (int)
    - col_id, the column id of the pixel (int)
    - row_id, the row id of the pixel (int)
    - x, the real component of the wave vector (int/float)
    - y, the imaginary component of the wave vector (int/float)
    Optionally the last column may be omitted, in which case all resulting
    wave vectors will have real values.

    Args:
        filename (str): Name of the file to read.

    Returns:
        list[Image]
    """
    df = read_csv(filename, names=('block_id', 'col_id', 'row_id', 'x', 'y'))
    if any(df['y']):
        df['value'] = df['x'].astype('complex') + complex(0, 1) * df['y'].astype('complex')
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
        """Construct an Image from a pandas.DataFrame.

        This DataFrame is expected to have at least the following columns:
        - col_id, the column index of a pixel (int),
        - row_id, the row index of a pixel (int),
        - value, the value of the wave vector at the pixel (int/float/complex)

        Args:
            df (pandas.DataFrame): DataFrame containing the image data.
            block_id (int/None): ID of the image.

        Returns:
            Image
        """
        i = cls(0, 0, block_id=block_id)
        values = df.sort_values(['row_id', 'col_id']).value.values
        n_cols = df.col_id.max() + 1
        unpacked = [values[x:x + n_cols] for x in range(0, len(values), n_cols)]
        i.data = array(unpacked, dtype=df.value.dtype.type)
        return i

    def to_df(self):
        """Construct a pandas.DataFrame from the Image.

        Returns:
            pandas.DataFrame
        """
        return DataFrame([
            {'row_id': row_id, 'col_id': col_id,
             'value': self.data[row_id, col_id], 'block_id': self.block_id}
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
