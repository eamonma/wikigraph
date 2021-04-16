import os
import fileinput
import re
from tqdm import tqdm

from wikigraph import wikitext
from wikigraph import partition_data


def process_partition(partition_file: str, index: list[int], p_points: list[int],
                      links_to_file: str, info_file: str) -> None:
    """Process the entire enwiki database and output it to the desired file

    Assumes that the dataset is partitioned
    """
    # Get the index and the partition_points
    # index = partition_data.read_index(index_file)
    # p_points = partition_data.read_index(partition_index_file)

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
    page_number = 1
    current_page = ''

    if os.path.exists(info_file[:-4] + '-' + partition_file[-8:-4] + '.csv'):
        os.remove(info_file[:-4] + '-' + partition_file[-8:-4] + '.csv')

    if os.path.exists(links_to_file[:-4] + '-' + partition_file[-8:-4] + '.csv'):
        os.remove(links_to_file[:-4] + '-' + partition_file[-8:-4] + '.csv')

    # f = open(info_file[-4:] + '-' +
    #                          partition_file[-8:-4] + '.csv', 'a')
    #                 f.write(title + ',' + redirect + ',' +
    #                         str(character_count) + ',' + str(last_edit) + '\n')
    #                 f.close()

    # with tqdm(total=20852797) as progressbar:
    f_path = info_file[:-4] + '-' + partition_file[-8:-4] + '.csv'
    g_path = links_to_file[:-4] + '-' + partition_file[-8:-4] + '.csv'

    f = open(f_path, "w")
    g = open(g_path, "w")

    # with open(f_path, "w"), open(g_path, "w") as f, g:
    for line in iterator_thing:
        current_page += line
        if count in offset_index:
            # Get the title
            title = wikitext.get_title(current_page).lower()
            # Get if the article is a redirect or not
            # ("" if not, the article it redirects to if so)
            redirect = wikitext.parse_redirect(current_page).lower()

            if not redirect:
                # Get the number of characters in the text of the article
                character_count = wikitext.char_count(current_page)
                # Get the timedelta between the last edit and 2021-01-01
                last_edit = wikitext.last_revision(current_page)

                # Write information if not redirect
                f.write(title + ',' + redirect + ',' +
                        str(character_count) + ',' + str(last_edit) + '\n')

                # Get a set of the links_to
                links_to = {i.lower()
                            for i in wikitext.collect_links(current_page)}

                # Write a list of edges
                g.write(title + ',' + ','.join(links_to).replace('\n',
                        '\\n').replace('\t', '\\t').replace('\r', '\\r') + '\n')
            else:
                # Write information if redirect
                f.write(title + ',' + redirect + ',,\n')

                # Write an empty list of edges since a redirect file will have no edges
                g.write(title + ',\n')

            # Reset the contents of the page
            current_page = ''
            # Update the progress bar
            # progressbar.update(1)

        # Increment the line number
        count += 1

    f.close()
    g.close()


if __name__ == '__main__':
    os.chdir(__file__[0:-len('wikigraph/process_wikitext.py')])
    import time
    import concurrent.futures

    partition_rel_dir = "partitioned_2"

    partitioned_files = os.listdir(f"data/processed/{partition_rel_dir}")

    index = partition_data.read_index('data/processed/wiki-index.txt')
    p_points = partition_data.read_index(
        f'data/processed/{partition_rel_dir}/partition-index.txt')

    start = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        processes = [executor.submit(process_partition, f'data/processed/{partition_rel_dir}/{file}',
                                     index,
                                     p_points,
                                     'data/processed/links_to.csv',
                                     'data/processed/info.csv')
                     for file in partitioned_files]

        for f in concurrent.futures.as_completed(processes):
            print(f.done())

        # f1 =
        # f2 = executor.submit(do_something, 1)
        # print(f1.result())
        # print(f.result())

        # for _ in range(10):
        #     p = multiprocessing.Process(target=do_something, args=[1.5])
        #     p.start()
        #     processes.append(p)

        # for process in processes:
        #     process.join()

    finish = time.perf_counter()
    print(f"Time taken: {round(finish - start, 2)}")

    # from experiments import versus_wtp

    # versus_wtp("")

    # finish = time.perf_counter()
    # print(f"{round(finish - start, 2)}")

    # f = open("../data/processed/info.csv", "a")
    # f.write("yee")
    # f.close()

    # process_partition('../data/processed/partitioned/enwiki-20210101-0002.xml',
    #                   '../data/processed/wiki-index.txt',
    #                   '../data/processed/partitioned/partition-index.txt',
    #                   'edge.csv',
    #                   'info.csv')
