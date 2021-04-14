import os
import timeit
import wikitextparser as wtp
import pprint
import sys
import re
import pytest

from wikigraph.wikitext import collect_links_wikitext

print(os.getcwd())
with open('data/raw/reduced/hundredk.xml', 'r') as reader:
    wikitext = reader.read()

collected_links = collect_links_wikitext(wikitext)

def test_collect_links_wikitext():
    """
    docstring
    """
    # random links that should be in it
    links = [
        "2012–13 UEFA Europa League",
        "Propargyl alcohol",
        "Category:American social commentators",
        "Second French Empire",
        "File:Banu Qurayza.png",
        "The Great Gatsby (2013 film)",
        "Image:Justus Sustermans - Portrait of Galileo Galilei (Uffizi).jpg"
        ]


    assert all([link in collected_links for link in links])

def test_not_collect_links_wikitext():
    """
    docstring
    """
    # random links that should not be in it
    links = [
        "David is very cool but this wouldn't be an appropriate wiki title",
        "Mario is very cool but this wouldn't be an appropriate wiki title",
        "Canucks wins",
        "Michelle Obama"
        ]

    assert all([link not in collected_links for link in links])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
