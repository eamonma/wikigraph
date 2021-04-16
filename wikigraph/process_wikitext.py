import os
from wikigraph import wikitext
from wikigraph import partition_data
from tqdm import tqdm


def process_it(data_file: str, index_file: str, partition_file: str, edge_file: str, info_file: str) -> None:
    """Process the entire enwiki database and output it to the desired file

    Assumes that the dataset is partitioned
    """
    index = partition_data.read_index(index_file)
    p_points = partition_data.read_index(partition_file)


if __name__ == '__main__':
    os.chdir(__file__[0:-len('process_wikitext.py')])
    # Example runner of
