import pytest
import wikitextparser as wtp

from wikigraph import wikitext
from wikigraph.experiments import versus_wtp

with open('data/raw/reduced/hundredk.xml', 'r') as reader:
    sample_wikitext = reader.read()

collected_links = wikitext.collect_links(sample_wikitext)


def test_collect_links():
    """
    test that linked article titles include all types of them
    """
    # random links that should be in it
    links = [
        "2012–13 UEFA Europa League",
        "Propargyl alcohol",
        "Category:American social commentators",
        "Second French Empire",
        "File:Banu Qurayza.png",
        "The Great Gatsby (2013 film)",
        "Image:Justus Sustermans - Portrait of Galileo Galilei (Uffizi).jpg",
        "Image:Methane-2D-stereo.svg",
        "Methane",
        "Paraffin (disambiguation)",
        "Tooth enamel",
        "Chelsea, London",
        "Category:April",
        "microphone"
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


with open('data/raw/reduced/animation.xml', 'r') as reader:
    animation_page = reader.read()

def test_char_count():
    extracted = wikitext.extract_content(animation_page)

    assert wikitext.char_count(animation_page) == 69345
    assert "[[Category:Film and video technology]]" in extracted
    assert extracted[len(extracted) -
                     len("[[Category:Film and video technology]]"):len(extracted)] == "[[Category:Film and video technology]]"


def test_last_revision():
    from datetime import datetime
    assert wikitext.last_revision(
        animation_page) == 45100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
