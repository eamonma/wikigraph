from wikitext import collect_links_wikitext
from experiments import versus_wtp
import wikitextparser as wtp

with open('../data/raw/reduced/hundredk.xml', 'r') as reader:
    wikitext = reader.read()


versus_wtp.time_versus("collect_links_wikitext(wikitext)",
            "wtp.parse(wikitext)",
            {"times": 1}, globals())

# versus_wtp.diff_lists([item for item in collect_links_wikitext(wikitext) if item],
#                        [l.title for l in wtp.parse(wikitext).wikilinks if l.title], io=True)
