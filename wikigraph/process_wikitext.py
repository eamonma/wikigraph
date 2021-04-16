import os
import csv
import fileinput
import re
from tqdm import tqdm
import concurrent.futures

from wikigraph import wikitext
from wikigraph import partition_data


def process_partition(partition_file: str, index: list[int], p_points: list[int],
                      links_file: str, info_file: str) -> None:
    """Process the entire enwiki database and output it to the desired file

    Assumes that the dataset is partitioned
    """
    # Get the partition number from the file number
    partition_number = int(partition_file[-8:-4])

    iterator_thing = fileinput.input([partition_file])

    if partition_number == 1:
        line_offset = 45

        # Getting rid of the preamble in the xml (only in the first partition)
        chop_line_count = 0
        for line in iterator_thing:
            if chop_line_count == 43:
                break
            chop_line_count += 1
    else:
        line_offset = p_points[partition_number - 2]

    # offset the index based on the partition number
    offset_index = {i - line_offset for i in index}

    count = 1
    current_page = ''

    if os.path.exists(info_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'):
        os.remove(info_file[:-4] + '-' + partition_file[-8:-4] + '.tsv')

    if os.path.exists(links_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'):
        os.remove(links_file[:-4] + '-' + partition_file[-8:-4] + '.tsv')

    f_path = info_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'
    g_path = links_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'

    f = open(f_path, "w")
    g = open(g_path, "w")

    for line in iterator_thing:
        current_page += line
        if count in offset_index:
            # Get the title
            title = wikitext.get_title(current_page)
            # Get if the article is a redirect or not
            # ("" if not, the article it redirects to if so)
            redirect = wikitext.parse_redirect(current_page)

            if not redirect:
                # Get the number of characters in the text of the article
                character_count = wikitext.char_count(current_page)
                # Get the timedelta between the last edit and 2021-01-01
                last_edit = wikitext.last_revision(current_page)

                # Write information if not redirect
                f.write(title + '\t' + redirect + '\t' +
                        str(character_count) + '\t' + str(last_edit) + '\n')

                # Get a set of the links and remove anything prefixed with 'File:' or 'file:'
                links = set(l for l in wikitext.collect_links(current_page)
                            if 'file:' not in l.lower())

                # Write a list of edges
                g.write(title + '\t' + '\t'.join(i.replace('\n', '\\n')
                                                 .replace('\t', '\\t')
                                                 .replace('\r', '\\r') for i in links) + '\n')
            else:
                # Write information if redirect
                f.write(title + '\t' + redirect + '\t\t\n')

                # Write an empty list of edges since a redirect file will have no edges
                g.write(title + '\t\n')

            # Reset the contents of the page
            current_page = ''
            # Update the progress bar
            # progressbar.update(1)

        # Increment the line number
        count += 1

    f.close()
    g.close()


def parallel_process_partition(data_dir: str = "data/processed", partition_rel_dir: str = "partitioned") -> None:
    """Run process_partition with councurrent processes
    """
    os.chdir(__file__[0:-len('wikigraph/process_wikitext.py')])

    partitioned_files = [partitioned_file for partitioned_file in os.listdir(
        f"{data_dir}/{partition_rel_dir}") if ".xml" in partitioned_file]

    index = partition_data.read_index(f'{data_dir}/wiki-index.txt')
    p_points = partition_data.read_index(
        f'{data_dir}/{partition_rel_dir}/partition-index.txt')

    partitioned_files.sort()
    print(partitioned_files)


    with concurrent.futures.ProcessPoolExecutor() as executor:
        processes = [executor.submit(process_partition, f'{data_dir}/{partition_rel_dir}/{file}',
                                     index,
                                     p_points,
                                     f'{data_dir}/graph/links.tsv',
                                     f'{data_dir}/graph/info.tsv')
                     for file in partitioned_files]

        for f in concurrent.futures.as_completed(processes):
            print(f"{f.done() and 'Done'}")

def collapse_redirects(links_file: str, info_file: str) -> dict:
    """Get rid of redirect links in info_file"""
    redirects = dict()
    links = dict()
    info = dict()

    # Getting all the redirects
    info_r = open(info_file, 'r')
    info_rows = csv.reader(info_r, delimiter='\t')
    for row in info_rows:
        if row[1] != '':
            redirects[row[0]] = row[1]
        else:
            info[row[0]] = [row[2], row[3]]

    # Getting all of the vertices and their edges
    links_r = open(links_rile, 'r')
    links_rows = csv.reader(links_r, delimiter='\t')
    for row in links_rows:
        links[row[0]] = set(row[1:-1])

    # Replacing redirect links with thier original
    for key in links:
        for element in links[key]:
            if element in redirects:
                element = redirects[element]

    # Writing to the info_file
    info_w = open(links_file, 'w')
    write = '\n'.join([title + '\t' + '\t'.join(info[title])
                       for title in info])
    info_w.write(write)
    info_w.close()

    # Writing to the links_file
    links_w = open(links_file, 'w')
    write = '\n'.join([title + '\t' + '\t'.join(links[title])
                       for title in links if title not in redirects])
    links_w.write(write)
    links_w.close()


if __name__ == '__main__':
    os.chdir(__file__[0:-len('wikigraph/process_wikitext.py')])
    import time

    parallel_process_partition("data/processed", "partitioned_2")
    # from experiments import versus_wtp

    # versus_wtp("")

    # finish = time.perf_counter()
    # print(f"{round(finish - start, 2)}")

    # f = open("../data/processed/info.tsv", "a")
    # f.write("yee")
    # f.close()

    # index = partition_data.read_index(f'data/processed_2/wiki-index.txt')
    # p_points = partition_data.read_index(
    #     f'data/processed_2/partitioned_2/partition-index.txt')

    parallel_process_partition("data/processed_2", "partitioned_2")

    # from partition_data import partition_on_num
    # partition_on_num('data/raw/reduced/million.xml',
    #                  'data/processed/wiki-index.txt',
    #                  10,
    #                  'data/processed_2/partitioned_2/partition-index.txt',
    #                  'data/processed_2/partitioned_2/million')

    # generate = True

    # if generate:
    #     index = partition_data.read_index('data/processed/wiki-index.txt')
    #     p_points = partition_data.read_index('data/processed/partitioned_2/partition-index.txt')

    #     process_partition('data/processed/partitioned_2/million-0002.xml',
    #                       index,
    #                       p_points,
    #                       'data/processed/graph/links.tsv',
    #                       'data/processed/graph/info.tsv')
    # else:
    #     collapse_redirects('data/processed/links-0002.tsv', 'data/processed/info-0002.tsv')

    # process_partition('../data/processed/partitioned/enwiki-20210101-0002.xml',
    #                   '../data/processed/wiki-index.txt',
    #                   '../data/processed/partitioned/partition-index.txt',
    #                   'edge.tsv',
    #                   'info.tsv')
