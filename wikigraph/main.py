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

    import process_wikitext

    process_wikitext.parallel_process_partition(
        data_dir="data/processed", partition_rel_dir="partitioned")

    # versus_wtp.diff_lists([item for item in collect_links(wikitext) if item],
    #                        [l.title for l in wtp.parse(wikitext).wikilinks if l.title], io=True)
