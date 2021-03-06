import os
import csv
import fileinput
import re
import shutil
from tqdm import tqdm
import concurrent.futures

from wikigraph import wikitext
from wikigraph import partition_data


def process_partition(partition_file: str, index: list[int], p_points: list[int],
                      links_file: str, info_file: str) -> None:
    """Process the entire enwiki database and output it to the desired file

    Assumes that the dataset is partitioned

    Example Run:
    >>> index = partition_data.read_index('data/processed/wiki-index.txt')
    >>> p_points = partition_data.read_index('data/processed/partitioned/partition-index.txt')
    >>> process_partition('data/processed/partitioned/enwiki-20210101-0001.xml',
    ...                   index,
    ...                   p_points,
    ...                   'data/processed/graph/wiki-links.tsv',
    ...                   'data/processed/graphs/wiki-info.tsv')
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

    # If the file already exists, delete it to overwrite it
    if os.path.exists(info_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'):
        os.remove(info_file[:-4] + '-' + partition_file[-8:-4] + '.tsv')

    # If the file already exists, delete it to overwrite it
    if os.path.exists(links_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'):
        os.remove(links_file[:-4] + '-' + partition_file[-8:-4] + '.tsv')

    # File writere paths
    f_path = info_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'
    g_path = links_file[:-4] + '-' + partition_file[-8:-4] + '.tsv'

    # Open file writer
    f = open(f_path, "w")
    g = open(g_path, "w")

    # i = 0

    for line in iterator_thing:
        current_page += line
        if count in offset_index:
            # Get the title
            title = wikitext.get_title(current_page)

            # Get if the article is a redirect or not
            # ("" if not, the article it redirects to if so)
            redirect = wikitext.parse_redirect(current_page)

            if not redirect:
                try:
                    # Get the number of characters in the text of the article
                    character_count = wikitext.char_count(current_page)
                except Exception as e:
                    character_count = 0

                try:
                    # Get the timedelta between the last edit and 2021-01-01
                    last_edit = wikitext.last_revision(current_page)
                except Exception as e:
                    last_edit = 0

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

    # Close the files
    f.close()
    g.close()


def parallel_process_partition(data_dir: str = "data/processed",
                               partition_rel_dir: str = "partitioned",
                               max_workers: int = 10) -> None:
    """Run process_partition with councurrent processes

    Example Run:
    >>> parallel_process_partition('data/processed', 'partitioned', max_workers=5)
    """
    os.chdir(__file__[0:-len('wikigraph/process_wikitext.py')])

    partitioned_files = [partitioned_file for partitioned_file in os.listdir(
        f"{data_dir}/{partition_rel_dir}") if ".xml" in partitioned_file]

    index = partition_data.read_index(f'{data_dir}/wiki-index.txt')
    p_points = partition_data.read_index(
        f'{data_dir}/{partition_rel_dir}/partition-index.txt')

    partitioned_files.sort()
    print(partitioned_files)

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        processes = [executor.submit(process_partition, f'{data_dir}/{partition_rel_dir}/{file}',
                                     index,
                                     p_points,
                                     f'{data_dir}/graph/links.tsv',
                                     f'{data_dir}/graph/info.tsv')
                     for file in partitioned_files]

        for f in concurrent.futures.as_completed(processes):
            print(f"{f.done() and 'Done'}")


def get_redirects(info_file: str, output: str) -> None:
    """Get the all of the redirect vertices
    """
    redirect = dict()

    # Getting redirects from the info_file
    print("Getting redirects...")
    for line in tqdm(fileinput.input(info_file, openhook=fileinput.hook_encoded("utf-8"))):
        row = line.split('\t')
        if row[1] != '':
            redirect[row[0]] = row[1]

    # Writing to the info_file
    redirect_w = open(output, 'w', encoding='utf8')
    write = '\n'.join([title + '\t' + redirect[title] for title in redirect])
    redirect_w.write(write)
    redirect_w.close()


def collapse_redirects(info_file: str, links_file: str, redirect_file: str,
                       info_file_output: str, links_file_output: str) -> None:
    """Get rid of redirect links in info_file

    Example Run:
    >>> collapse_redirects('data/processed/graph/wiki-info.tsv',
    ...                   'data/processed/graph/wiki-links.tsv',
    ...                   'data/processed/graph/redirect-info.tsv'
    ...                   'data/processed/graph/wiki-info-collapsed.tsv',
    ...                   'data/processed/graph/wiki-links-collapsed.tsv')
    """
    # Getting redirect information
    redirect = dict()
    print("Reading redirect information...")
    for line in tqdm(fileinput.input(redirect_file, openhook=fileinput.hook_encoded("utf-8"))):
        row = line.split('\t')
        redirect[row[0]] = row[1]

    # Collapsing the redirects in links_w
    links_w = open(links_file_output, 'w', encoding='utf8')
    print("Collaping redirects in links...")
    for line in tqdm(fileinput.input(links_file, openhook=fileinput.hook_encoded("utf-8"))):
        row = line[:-1].split('\t')

        if row[0] not in redirect:
            for i in row[1:]:
                if i in redirect:
                    i = redirect[i]

            links_w.write('\t'.join(row) + '\n')

    links_w.close()

    info_w = open(info_file_output, 'w', encoding='utf8')
    print("Collaping redirects in info...")
    for line in tqdm(fileinput.input(info_file, openhook=fileinput.hook_encoded("utf-8"))):
        row = line.split('\t')

        if row[0] not in redirect:
            info_w.write(line)

    info_w.close()


def concatenate_files(file_locations: str,
                      out_info_file: str = 'wiki-info.tsv',
                      out_links_files: str = 'wiki-links.tsv',
                      delete_remnants: bool = False) -> None:
    """Concatenate the info and links files generated from the computation into one file each

    Example Run
    >>> concatenate_files('data/processed/graph', 'wiki-info.tsv', 'wiki-links.tsv')
    """
    # os.chdir(__file__[0:-len('wikigraph/process_wikitext.py')] + '/data/processed')

    # Get the info and links files
    info_files = sorted([info_file
                         for info_file in os.listdir(file_locations)
                         if "info" in info_file])
    links_files = sorted([links_file
                          for links_file in os.listdir(file_locations)
                          if "links" in links_file])

    os.chdir(file_locations)

    # Concatenate the info files
    print("Concatenating Info Files...")
    with tqdm(total=len(info_files)) as progressbar:
        target_info_file_name = out_info_file
        shutil.copy(info_files[0], target_info_file_name)
        with open(target_info_file_name, 'a') as out_file:
            for source_file in info_files[1:]:
                with open(source_file, 'r') as in_file:
                    shutil.copyfileobj(in_file, out_file)
                    in_file.close()
                    progressbar.update(1)
            out_file.close()
        progressbar.update(1)

    # Concatenate the links files
    print("Concatenating Links Files...")
    with tqdm(total=len(links_files)) as progressbar:
        target_links_file_name = out_links_files
        shutil.copy(links_files[0], target_links_file_name)
        with open(target_links_file_name, 'a') as out_file:
            for source_file in links_files[1:]:
                with open(source_file, 'r') as in_file:
                    shutil.copyfileobj(in_file, out_file)
                    in_file.close()
                    progressbar.update(1)
            out_file.close()
        progressbar.update(1)

    if delete_remnants:
        for i in info_files:
            os.remove(i)

        for i in links_files:
            os.remove(i)


if __name__ == '__main__':
    os.chdir(__file__[0:-len('wikigraph/process_wikitext.py')])

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
