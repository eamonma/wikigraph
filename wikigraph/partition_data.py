"""Create an index of all the opening page tags (<page>) in the xml dataset

Specifications:
 - FILE_LINE_COUNT:
    This is the line count of the file that is being used. For enwiki (the full dataset),
    this variable will be 121820507. For million.xml it will be 1000000, for hundredk.xml
    it will be 98727.
 - create_index('path/to/enwiki.xml'):
    This function returns a list of integers of all the opening page tags in the database.
 - write_index(list[int], 'path/to/new-index.txt'):
    This functoin writes a list of integers to a file.
 - read_index('path/to/index.txt'):
    This function reads in an index save file and returns them as a list of integers.
 - round_to_list(number, list[int]):
    This function rounds a number to the nearest number that is lower than it in the list.
 - get_partition_points_num(number_of_partitions, list[int]):
    This function returns a list of partition points based on the number of partitions requested
 - get_partition_points_size(size_of_partition, list[int]):
    This function returns a list of partition points based on the maximum size of partition
    requested
 - partition('path/to/enwiki.xml', partition_points, 'path/to/output')
    This function outputs partitions based on all the information it reieves

Example of use:
In this example, we will create 100 partitions of enwiki-20210101-pages-articles-multistream.xml.
We will assume that we are currently in the wikigraph directory. Modify paths as needed.

>>> index = create_index('../data/raw/enwiki-20210101-pages-articles-multistream.xml')
# This will print a progress bar and save the information to the index variable

>>> write_index(index, '../data/processed/wiki-index.txt')
# This line is optional, but it is recommended as regenerating the index takes a lot o time

>>> read_index('../data/processed/wiki-index.txt')
# This line is only needed if you did not create the index. If you have an index file generated,
# then use this, if you do not then create a new index

>>> partition_points = get_partition_points_num(100, index)
# This will generate a list of partition points. If you want maximum size of each partition instead
# of line count, then you can use the gat_partition_points_size(100000, index) instead to get a
# maximum file size of 100,000 lines.

>>> partition('../data/raw/enwiki-20210101-pages-articles-multistream.xml', partition_points,
...           '../data/processed/partitioned/enwiki-20210101-pages-articles-multistream')
# This will generate the files enwiki-20210101-pages-articles-multistream-0XXX.xml, where XXX is
# the partition number, in the directory data/processed/partitioned/
"""
import os
import fileinput
from tqdm import tqdm

FILE_LINE_COUNT = 1218205075        # enwiki-20210101[...].xml
# FILE_LINE_COUNT = 98727           # hundredk.xml
# FILE_LINE_COUNT = 1000001         # muillion.xml


def create_index(filename: str) -> list[int]:
    """Find the line number of every <page> in the file, and return it in a list"""
    # Keeps a track of number of lines in the file
    count = 1
    line_numbers = []

    # Progress bar code
    print("Generating Index File...")
    with tqdm(total=FILE_LINE_COUNT) as progressbar:
        # Read file line by line for ram management
        for lines in fileinput.input(filename, openhook=fileinput.hook_encoded("utf-8")):
            # If the line is an opening page tag, record it
            if '<page' in lines:
                line_numbers.append(count)
            count += 1
            # Advance the progress bar
            progressbar.update(1)

    return line_numbers


def write_index(index: list[int], filename: str) -> None:
    """Write a list of integers to a file, one integer per line"""
    f = open(filename, 'w')
    print("Writing Index File...")
    f.write('\n'.join([str(i) for i in tqdm(index)]))
    f.close()


def read_index(index_file: str) -> list[int]:
    """Read an index file, one number per line, into a list of integers"""
    f = open(index_file, 'r')
    line_strings = f.readlines()
    line_numbers = []

    print("Reading Index File...")
    for s in tqdm(line_strings):
        line_numbers.append(int(s))

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

    print("Generating partition points...")
    for i in tqdm(range(num_partitions)):
        # Add a partition close to (just under) the approximate location
        selected_partition_points.append(round_to_list(
            (i + 1) * approx_partition_size, index))
        # if i == 0:
        #     selected_partition_points.append(
        #         round_to_list(approx_partition_size, index))
        # else:
            # selected_partition_points.append(
            #     round_to_list(approx_partition_size + selected_partition_points[-1], index))

    # Add the last partition point
    selected_partition_points[len(
        selected_partition_points) - 1] = FILE_LINE_COUNT + 1

    return selected_partition_points


def get_partition_points_size(lines_per_partition: int, index: list[int]):
    """Return the line numbers where the dataset will be partitioned at.
    The partitions will be selected such that all partitions will be less than
    or equal to =lines_per_partition= lines long"""
    # Get the approximate number of partitions being created
    approx_num_partitions = FILE_LINE_COUNT // lines_per_partition
    selected_partition_points = []

    print("Generating partition points...")
    for i in tqdm(range(approx_num_partitions)):
        # Add a partition close to (just under) the approximate location
        if i == 0:
            selected_partition_points.append(
                round_to_list(lines_per_partition, index))
        else:
            selected_partition_points.append(
                round_to_list(lines_per_partition + selected_partition_points[-1], index))

    # Add the last partition point
    selected_partition_points.append(FILE_LINE_COUNT + 1)

    # if (lst[-1] - lst[-2]) > lines_per_partition then we select a mid point and insert it at -1
    if selected_partition_points[-1] - selected_partition_points[-2] > lines_per_partition:
        midpoint = (
            selected_partition_points[-1] + selected_partition_points[-2]) // 2
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
    with tqdm(total=FILE_LINE_COUNT) as progressbar:
        for line in fileinput.input(filename, openhook=fileinput.hook_encoded("utf-8")):
            if count in partition_points:
                outfile = open(output + "-%04d" % n + '.xml', 'w')
                outfile.write(''.join(current_partition))
                outfile.close()

                n += 1
                current_partition = []

            current_partition.append(line)
            count += 1
            progressbar.update(1)


def partition_on_num(data_file: str, index_file: str, num: int, out_partition_file: str,
                     output: str) -> None:
    """Run all the methods for partitioning the data

    Example call:
    >>> partition_on_num('../data/raw/reduced/hundredk.xml',
    ...                  '../data/processed/wiki-index.txt',
    ...                  10,
    ...                  '../data/processed/partitioned/partition-index.txt',
    ...                  '../data/processed/partitioned/hundredk', )
    """
    index = read_index(index_file)
    p_points = get_partition_points_num(num, index)
    write_index(p_points, out_partition_file)
    partition(data_file, p_points, output)


def partition_on_size(data_file: str, index_file: str, size: int, out_partition_file: str, output: str) -> None:
    """Run all the methods for partitioning the data

    Example call:
    >>> partition_on_size('../data/raw/reduced/hundredk.xml',
    ...                   '../data/processed/wiki-index.txt',
    ...                   1000,
    ...                   '../data/processed/partitioned/partition-index.txt',
    ...                   '../data/processed/partitioned/hundredk', )
    """
    index = read_index(index_file)
    p_points = get_partition_points_size(size, index)
    write_index(p_points, out_partition_file)
    partition(data_file, p_points, output)


if __name__ == '__main__':
    os.chdir(__file__[0:-len('wikigraph/partition_data.py')])

    # NOTE: Don't have these on all the time
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    # NOTE: These others are fine
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 1000,
        'disable': ['E1136'],
        'extra-imports': ['csv', 'networkx', 'os', 'graph_implementation'],
        'allowed-io': ['load_review_graph'],
        'max-nested-blocks': 4
    })
