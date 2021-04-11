import timeit
import wikitextparser as wtp
import os
import pprint
import sys
import re

wikitext = ""

print(os.getcwd())

with open('data/raw/million.xml', 'r') as reader:
    wikitext = reader.read()
# with open('../tests/wikitext/sample_wikitext.txt', 'r') as reader:
#     wikitext = reader.read()

# wikitext = "'''Anarchism''' is a [[political philosophy]] and [[Political movement|movement]] that is sceptical of [[authority]] and rejects all involuntary, coercive forms of [[hierarchy]] San Francisco also has [[public transport]]ation. Examples include [[bus]]es, [[taxicab]]s, and [[tram]]s [[Wikipedia:Manual of Style#Italics]] is a link to a section within another page. [[#Links and URLs]] is a link to another section on the current page. [[#Links and URLs|Links and URLs]] is a link to the same section without showing the # symbol. [[Wikipedia:Manual of Style#Italics|Italics]] is a piped link to a section within another page."


def collect_links_wikitext(wikitext: str) -> list:
    """Collect links given wikitext
    Find tags containing "[[]]" and parse within it.
    Maintains case.

    >>> collect_links_wikitext("[[political philosophy]][[Political movement|movement]][[authority]][[hierarchy]]")
    ['political philosophy', 'Political movement', 'authority', 'hierarchy']
    >>> collect_links_wikitext("[[public transport|public transportation]][[kingdom (biology)|]][[Seattle, Washington|]][[Wikipedia:Manual of Style (headings)|]]")
    ['public transport', 'kingdom (biology)', 'Seattle, Washington',
                                   'Wikipedia:Manual of Style (headings)']
    >>> collect_links_wikitext("[[public transport]]ation [[bus]]es, [[taxicab]]s, and [[tram]]s")
    ['public transport', 'bus', 'taxicab', 'tram']
    >>> collect_links_wikitext("[[Wikipedia:Manual of Style#Italics]][[#Links and URLs]][[#Links and URLs|Links and URLs]][[Wikipedia:Manual of Style#Italics|Italics]]")
    ['Wikipedia:Manual of Style', 'Wikipedia:Manual of Style']
    """
    wikilinks = list()
    # items = re.findall("\[\[[\S\s]*?\]\]", wikitext)
    items = re.findall("\[\[(.*?)\]\]", wikitext)
    # wikilinks = [_parse_wikilink(wikilink) or '' for wikilink in items]
    for wikilink in items:
        wikilinks += _parse_wikilink(wikilink) or ''

    return wikilinks


def _parse_wikilink(wikilink: str) -> list:
    """Return the linked article.
    Return None if links to section within page
    """

    # Link, section on same page
    try:
        if wikilink[0] == "#":
            return

        if wikilink[0] == "F" and wikilink[:5] == "File:" or wikilink[0] == "I" and wikilink[:6] == "Image:":
            pipe_index = wikilink.find("|")
            lsbr_index = wikilink.find("[[")
            if not (lsbr_index == -1 and pipe_index == -1):
                parsed_sublink = _parse_wikilink(wikilink[lsbr_index + 2:])
            else:
                parsed_sublink = wikilink
            return [wikilink if pipe_index == -1 else wikilink[:pipe_index]]
            + (parsed_sublink if lsbr_index != -1 and parsed_sublink else [])

        # ===Link, renamed...===

        # ...section on different page
        hash_index = wikilink.find("#")
        if hash_index != -1:
            # if "Naming conventions" in wikilink:
            #     print(wikilink, hash_index, len(wikilink))
            pipe_index = wikilink.find("|")
            if pipe_index != -1 and pipe_index < hash_index:
                # print(wikilink, hash_index, len(wikilink))
                return [wikilink[:pipe_index]]
            return [wikilink[:hash_index]]

        # ...renamed, without section link (#)
        pipe_index = wikilink.find("|")
        if pipe_index != -1:
            return [wikilink[:pipe_index]]

        # ...not renamed
        return [wikilink]
    except Exception as e:
        print(wikilink, e)


# def test_collect_links_wikitext():
#     assert [link.title for link in wtp.parse(
#         wikitext).wikilinks] == collect_links_wikitext(wikitext)

# print(_parse_wikilink(
#     "File:United States Navy Band - God Save the Queen.ogg"))

# test_collect_links_wikitext()

