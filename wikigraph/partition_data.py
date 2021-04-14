#!/usr/bin/env python3
"""Create an index of all the opening page tags (<page>) in the xml dataset"""
import os
import fileinput
from alive_progress import alive_bar

# FILE_LINE_COUNT = 1218205075
FILE_LINE_COUNT = 98727

def create_index(filename: str) -> list[int]:
    """Find the line number of every <page> in the file, and return it in a list"""
    #keeps a track of number of lines in the file
    count = 1
    line_numbers = []

    # Progress bar code
    print("Generating Index File...")
    with alive_bar(FILE_LINE_COUNT) as progressbar:
        # Read file line by line for ram management
        for lines in fileinput.input([filename]):
            # If the line is an opening page tag, record it
            if '<page>' in lines:
                line_numbers.append(count)
            count += 1
            # Advance the progress bar
            progressbar()

    return line_numbers


def write_index(line_numbers: list[int], filename: str) -> None:
    """Write a list of integers to a file, one integer per line"""
    f = open(filename, 'w')
    f.write('\n'.join([str(i) for i in line_numbers]))
    f.close()


def read_index(index_file: str) -> list[int]:
    """Read an index file, one number per line, into a list of integers"""
    f = open(index_file, 'r')
    line_strings = f.readlines()
    line_numbers = []

    print("Reading Index File...")
    with alive_bar(len(line_strings)) as progressbar:
        for s in line_strings:
            line_numbers.append(int(s))
            progressbar()

    return line_numbers


def round_to_list(number: int, index: list[int]) -> int:
    """Round down =number= to the nearest element less than =number= in =index=

    -1 signifies that the element is larger than all other elements in the list
    and thus the partition should should go to the end of the file

    >>> round_to_list(30, [1, 20, 23, 25, 40])
    25
    >>> round_to_list(20, [1, 20, 23, 25, 40])
    20
    >>> round_to_list(41, [1, 20, 23, 25, 40])
    -1
    """
    for i, _ in enumerate(index):
        if index[i] > number:
            return index[i - 1]

    return -1


def get_partition_points_num(num_partitions: int, index: list[int]) -> list[int]:
    """Return the line numbers where the dataset will be partitioned at.
    The length of this list will be =num_partitions="""
    # Get the approximate size of each partition
    approx_partition_size = FILE_LINE_COUNT // num_partitions
    selected_partition_points = []

    print("Generating Partition Points...")
    with alive_bar(num_partitions) as progressbar:
        for i in range(num_partitions):
            # Add a partition close to (just under) the approximate location

            # NOTE: less consistent but less outliers
            # selected_partition_points.append(round_to_list((i + 1) * approx_partition_size, index))

            # NOTE: very consistent except for the last one, which is bigger
            if i == 0:
                selected_partition_points.append(round_to_list(approx_partition_size, index))
            else:
                selected_partition_points.append(
                    round_to_list(approx_partition_size + selected_partition_points[-1], index))

            progressbar()

    # Add the last partition point
    selected_partition_points[len(selected_partition_points) - 1] = FILE_LINE_COUNT + 1

    return selected_partition_points


def get_partition_points_size(lines_per_partition: int, index: list[int]):
    """Return the line numbers where the dataset will be partitioned at.
    The partitions will be selected such that all partitions will be less than
    or equal to =lines_per_partition= lines long"""
    # Get the approximate number of partitions being created
    approx_num_partitions = FILE_LINE_COUNT // lines_per_partition
    selected_partition_points = []

    print("Generating Partition Points...")
    with alive_bar(approx_num_partitions) as progressbar:
        for i in range(approx_num_partitions):
            # Add a partition close to (just under) the approximate location
            if i == 0:
                selected_partition_points.append(round_to_list(lines_per_partition, index))
            else:
                selected_partition_points.append(
                    round_to_list(lines_per_partition + selected_partition_points[-1], index))

            progressbar()

    # Add the last partition point
    selected_partition_points.append(FILE_LINE_COUNT + 1)

    # if (lst[-1] - lst[-2]) > lines_per_partition then we select a mid point and insert it at -1
    if selected_partition_points[-1] - selected_partition_points[-2] > lines_per_partition:
        midpoint = (selected_partition_points[-1] + selected_partition_points[-2]) // 2
        new_point = round_to_list(midpoint, index)
        selected_partition_points.insert(-1, new_point)

    return selected_partition_points


def partition(filename: str, partition_points: list[int], output: str) -> None:
    """Partition the dataset based on the values in =partition_points= and write the output as:

    output-000X.xml         , where X is the partition number

    Preconditions:
        - output does not end in .xml
    """
    count = 1
    current_partition = []
    n = 1

    print("Partitioning Dataset...")
    with alive_bar(FILE_LINE_COUNT + 1) as progressbar:
        for line in fileinput.input([filename]):
            if count in partition_points:
                outfile = open(output + "-%04d"%n+ 'b.xml', 'w')
                outfile.write(''.join(current_partition))
                outfile.close()

                n += 1
                current_partition = []

            current_partition.append(line)
            count += 1
            progressbar()


if __name__ == '__main__':
    os.chdir(__file__[0:-len('partition_data.py')])
    # # Index full wikitext database
    # write_index(create_index('../data/raw/enwiki-20210101-pages-articles-multistream.xml'),
    #             '../data/processed/wiki-index.txt')

    # # Index million wikitext database
    # write_index(create_index('../data/raw/reduced/million.xml'),
    #            '../data/processed/wiki-index.txt')

    # Partition smaller datasets
    ind = read_index('../data/processed/wiki-index.txt')

    # Partition based on number of partitions
    p_points = get_partition_points_num(10, ind)

    # # Partition based on size of partitions
    # p_points = get_partition_points_size(10000, ind)

    # partition(10, '../data/raw/reduced/million.xml', p_points,
    #           '../data/processed/partitioned/million')
    partition('../data/raw/reduced/hundredk.xml', p_points,
              '../data/processed/partitioned/hundredk')

    # # Partition full dataset
    # ind = read_index('../data/processed/wiki-index.txt')

    # # Partition based on number of partitions
    # p_points = get_partition_points_num(100, ind)

    # # Partition based on size of partitions
    # p_points = get_partition_points_size(10000, ind)

    # partition('../data/raw/enwiki[...].xml', p_points,
    #           '../data/processed/partitioned/full')
