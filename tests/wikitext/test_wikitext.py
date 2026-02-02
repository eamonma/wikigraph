import pytest
import wikitextparser as wtp

from wikigraph import wikitext
from wikigraph.experiments import versus_wtp

with open('tests/wikitext/anarchism.txt', 'r') as reader:
    sample_wikitext = reader.read()

# Extract the first page's wikitext content before the closing </text> tag.
sample_wikitext = sample_wikitext.partition("</text>")[0]

collected_links = wikitext.collect_links(sample_wikitext)


def test_collect_links():
    """
    test that linked article titles include all types of them
    """
    # random links that should be in it
    links = [
        "political philosophy",
        "Political movement",
        "State (polity)",
        "libertarian Marxism",
        "libertarian socialism",
        "history of anarchism",
        "Spanish Civil War",
        "File:WilhelmWeitling.jpg",
        "File:Bakunin.png",
        "Anarchist federalism",
        "Anarchy Archives",
        "Category:Anarchism",
        "Category:Political ideologies",
        "Category:Socialism"
    ]

    assert all(link in collected_links for link in links)


def test_not_collect_links():
    """
    test that linked article titles do not include ones that shouldn't be there
    """
    # random links that should not be in it
    links = [
        "David is very cool but this wouldn't be an appropriate wiki title",
        "Mario is very cool but this wouldn't be an appropriate wiki title",
        "Canucks wins",
        "Michelle Obama",
        "Ansel Adams",
    ]

    assert all(link not in collected_links for link in links)


def test_parse_wikilink():
    """
    test that wikilink parsing is working appropriately
    """
    matched_links = [
        "Wikipedia:Manual of Style#Italics",
        "Image:Justus Sustermans - Portrait of Galileo Galilei(Uffizi).jpg | left | thumb | upright | [[Galileo",
        "File:1967 Mantra-Rock Dance Avalon poster.jpg|thumb|right|upright|The [[Mantra-Rock Dance"
    ]

    expected_links = [
        "Wikipedia:Manual of Style",
        "Image:Justus Sustermans - Portrait of Galileo Galilei(Uffizi).jpg ",
        "Galileo",
        "File:1967 Mantra-Rock Dance Avalon poster.jpg",
        "Mantra-Rock Dance"
    ]

    parsed_links = []
    for link in matched_links:
        parsed_links += wikitext.parse_wikilink(link)

    assert parsed_links == expected_links


anarchism_page = (
    "<page>\n"
    "  <title>Anarchism</title>\n"
    "  <revision>\n"
    "    <timestamp>2017-06-05T04:18:18Z</timestamp>\n"
    f"    <text xml:space=\"preserve\">{sample_wikitext}</text>\n"
    "    <sha1>t7eab8s09kwusxrq46aqc8o2o8tvme1</sha1>\n"
    "    </revision>\n"
    "  </page>"
)

def test_char_count():
    extracted = wikitext.extract_content(anarchism_page)

    assert wikitext.char_count(anarchism_page) == 96486
    assert "[[Category:Socialism]]" in extracted
    assert extracted.endswith("[[Category:Socialism]]")


def test_last_revision():
    from datetime import datetime
    timestamp = "2017-06-05T04:18:18Z"
    # Mirror last_revision's reference date and seconds component behavior.
    delta_seconds = (datetime.fromisoformat("2021-01-01T00:00:01+00:00").replace(tzinfo=None) -
                     datetime.fromisoformat(
                         timestamp.replace("Z", "+00:00")).replace(tzinfo=None)).total_seconds()
    expected = int(delta_seconds) % (24 * 60 * 60)
    assert wikitext.last_revision(
        anarchism_page) == expected


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
