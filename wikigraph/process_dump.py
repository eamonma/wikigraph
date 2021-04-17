from wikigraph import partition_data, process_wikitext, graph_implementation
import os


def process_xml(xml_path: str = "data/raw/enwiki-20210101-pages-articles-multistream.xml",
                partitions: int = 80) -> None:
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

    process_wikitext.concatenate_files('data/processed/graph')

    process_wikitext.get_redirects('data/processed/graph/wiki-info.tsv',
                                   'data/processed/graph/redirects.tsv')

    process_wikitext.collapse_redirects('data/processed/graph/wiki-info.tsv',
                                        'data/processed/graph/wiki-links.tsv',
                                        'data/processed/graph/redirects.tsv',
                                        'data/processed/graph/wiki-info-collapsed.tsv',
                                        'data/processed/graph/wiki-links-collapsed.tsv')

    g = graph_implementation.load_graph('data/processed/graph/wiki-info-collapsed.tsv', 'data/processed/graph/wiki-links-collapsed.tsv')
    net = g.to_pyvis(10000)
    net.show('graph.html')


if __name__ == "__main__":
    process_xml("data/raw/enwiki-20210101-pages-articles-multistream.xml")
    # process_xml("data/.processed/partitioned/enwiki-20210101-0001.xml")
