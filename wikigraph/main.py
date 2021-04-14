from wikitext import collect_links
from experiments import versus_wtp
import wikitextparser as wtp

with open('../data/raw/reduced/million.xml', 'r') as reader:
    wikitext = reader.read()


versus_wtp.time_versus("collect_links(wikitext)",
            "wtp.parse(wikitext)",
            {"times": 10}, globals())

# versus_wtp.diff_lists([item for item in collect_links(wikitext) if item],
#                        [l.title for l in wtp.parse(wikitext).wikilinks if l.title], io=True)
