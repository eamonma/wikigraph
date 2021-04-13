#!/usr/bin/env python3
"""Create an index of all the opening page tags (<page>) in the xml dataset"""
import os
import fileinput

def index_file(filename: str) -> list[int]:
    """Find the line number of every <page> in the file, and return it in a list"""
    #keeps a track of number of lines in the file
    count = 1
    line_numbers = []
    for lines in fileinput.input([filename]):
        if '<page>' in lines:
            line_numbers.append(count)

        count += 1

    return line_numbers


def write_index(line_numbers: list[int], filename: str) -> None:
    """Write a list of integers to a file, one integer per line"""
    f = open(filename, 'w')
    f.write('\n'.join([str(i) for i in line_numbers]))
    f.close()


if __name__ == '__main__':
    os.chdir(__file__[0:-len('create_index.py')])
    write_index(index_file('../data/raw/enwiki-20210101-pages-articles-multistream.xml'),
                '../data/processed/wiki_index.txt')
    # write_index(index_file('../data/raw/reduced/million.xml'),
    #            '../data/processed/wiki_index.txt')
