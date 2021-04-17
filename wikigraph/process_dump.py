from wikigraph import partition_data, process_wikitext
import os


def process_xml(xml_path: str = "data/raw/enwiki-20210101-pages-articles-multistream.xml",
                partitions: int = 10) -> None:
    """
    Create XML index
    Create partition index
    Partition XML

    Preconditions:
        - File name ends with .xml
        - File tails with </page> and </mediawiki>
    """
    dir_path = os.path.dirname(os.path.realpath(
        __file__[0:-len('process_dump.py')]))

    partitioned_dir = f"{dir_path}/data/processed/partitioned"
    graph_dir = f"{dir_path}/data/processed/graph"

    if not os.path.exists(partitioned_dir):
        os.mkdir(partitioned_dir, 0o755)

    if not os.path.exists(graph_dir):
        os.mkdir(graph_dir, 0o755)

    # index = partition_data.create_index(xml_path)
    # partition_data.write_index(index, 'data/processed/wiki-index.txt')

    partition_data.partition_on_num(xml_path,
                                    'data/processed/wiki-index.txt',
                                    partitions,
                                    'data/processed/partitioned/partition-index.txt',
                                    f"""data/processed/partitioned/
                                    {xml_path[xml_path.rindex("/") + 1 : xml_path.rindex(".xml")]}""")

    process_wikitext.parallel_process_partition()


if __name__ == "__main__":
    process_xml("data/raw/enwiki-20210101-pages-articles-multistream.xml")
    # process_xml("data/.processed/partitioned/enwiki-20210101-0001.xml")
