from experiments import versus_wtp
import wikitextparser as wtp
import os
# with open('../data/raw/reduced/million.xml', 'r') as reader:
#     wikitext = reader.read()


# versus_wtp.time_versus("collect_links(wikitext)",
#             "wtp.parse(wikitext)",
#             {"times": 10}, globals())

if __name__ == "__main__":
    os.chdir(__file__[0:-len('wikigraph/main.py')])
    # assume that the following data is in place, from project root:
    # data/raw/enwiki-20210101-pages-articles-multistream.xml
    # for tests
    # data/raw/reduced/anarchism.txt
    # data/raw/reduced/animation.xml

    # ====to test on smaller datasets====
    # data/raw/reduced/k.xml
    # data/raw/reduced/ninepointthreek.xml
    # data/raw/reduced/hundredk.xml
    # data/raw/reduced/million.xml

    # from process_dump import process_xml

    # process_xml("data/raw/enwiki-20210101-pages-articles-multistream.xml")

    # import partition_data

    # partition_data.partition_on_num('data/raw/enwiki-20210101-pages-articles-multistream.xml',
    #                                 'data/processed/wiki-index.txt',
    #                                 80,
    #                                 'data/processed/partitioned/partition-index.txt',
    #                                 'data/processed/partitioned/enwiki-20210101-pages-articles-multistream.xml')

    # from wikigraph import partition_data

    # index = partition_data.read_index(f'data/processed/wiki-index.txt')
    # p_points = partition_data.read_index(
    #     f'data/processed/partitioned/partition-index.txt')

    # from process_dump import process_xml

    # process_wikitext.parallel_process_partition(
    #     data_dir="data/processed", partition_rel_dir="partitioned")

    # versus_wtp.diff_lists([item for item in collect_links(wikitext) if item],
    #                        [l.title for l in wtp.parse(wikitext).wikilinks if l.title], io=True)

    from process_wikitext import collapse_redirects

    # get_redirects("data/processed/graph/wiki-info.tsv",
    #               "data/processed/graph/redirects.tsv")

    collapse_redirects("data/processed/graph/wiki-info.tsv",
                       "data/processed/graph/wiki-links.tsv",
                       "data/processed/graph/redirects.tsv",
                       "data/processed/graph/wiki-info-collapsed.tsv",
                       "data/processed/graph/wiki-links-collapsed.tsv")

"""Main file to run setup and program"""
import os
import sys
import datetime

if __name__ == '__main__':
    # Change directory to the src dir. This is for file paths to work properly.
    os.chdir(__file__[0:-7])

    # Loop to keep running the prompt until the user choses to quit.
    continue_running = True
    while continue_running:
        print('\nWhat would you like to do?\n' +
              '\t[1] setup the datasets\n' +
              '\t[2] run the program\n' +
              '\t[3] run the program (compatibility mode)\n' +
              '\t[4] quit\n\n'
              'Choice: ', end='')

        # Ensure that the user enters either 1, 2, or 3.
        user_input = ''
        while user_input not in {'1', '2', '3', '4'}:
            user_input = input()

            # If the input is not valid, print an error message.
            if user_input not in {'1', '2', '3', '4'}:
                print('Invalid Input: Please either select 1 2, 3, or 4\n')
            else:
                print()

        # If the user enters 1, download and process the data.
        if user_input == '1':
            download_and_process_data()
        elif user_input == '2':  # If the user enters 2, run the program gui.
            # If all of the downloaded files are in place, then allow the program to run.
            # If not, then print an error.
            if all({'cdd.txt' in os.listdir('../data/raw/'),
                    'co2-concentration-long-term.csv' in os.listdir(
                        '../data/raw'),
                    'temperature-anomaly.csv' in os.listdir('../data/raw'),
                    'cdd.tsv' in os.listdir('../data/processed'),
                    'annual_average_temperature.csv' in os.listdir(
                        '../data/processed'),
                    'global_average_co2.csv' in os.listdir('../data/processed')}):
                print('Loading...')
                everything.run_system(False)
                print('Running in browser...')
            else:
                print('ERROR: Please setup the datasets before running ' +
                      'the program (see instructions)')
        elif user_input == '3':  # If the user enters 3, run the program gui in compatibility mode
            # If all of the downloaded files are in place, then allow the program to run.
            # If not, then print an error.
            if all({'cdd.txt' in os.listdir('../data/raw/'),
                    'co2-concentration-long-term.csv' in os.listdir(
                        '../data/raw'),
                    'temperature-anomaly.csv' in os.listdir('../data/raw'),
                    'cdd.tsv' in os.listdir('../data/processed'),
                    'annual_average_temperature.csv' in os.listdir(
                        '../data/processed'),
                    'global_average_co2.csv' in os.listdir('../data/processed')}):
                print('Loading...')
                everything.run_system(True)
                print('Running in browser... (compatibiliy mode)')
            else:
                print('ERROR: Please setup the datasets before running ' +
                      'the program (see instructions)')
        elif user_input == '4':
            continue_running = False
