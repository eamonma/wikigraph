import re
import os
import wikitextparser as wtp
import timeit
from datetime import datetime


def extract_information_from_wikitext(wikitext: str) -> dict:
    """Extract information from wikitext string provided. This will be things like word count, etc.
    We can either write one function for each of them (less complex code, higher time complexity) or
    we can write one function that will use one loop cycle to do many things, making the code less
    complex (not asymptotically, but in the actually real running time)
    """
    if "<redirect" in wikitext:
        redir_index = wikitext.find("<redirect")
        pass
        # todo
    raise NotImplementedError()


def collect_links_wikitext(wikitext: str) -> list:
    """Collect links given wikitext
    Find tags containing "[[]]" and parse within it.
    Maintains case.

    >>> collect_links_wikitext(\
    "[[political philosophy]][[Political movement|movement]][[authority]][[hierarchy]]") == \
    ['political philosophy', 'Political movement', 'authority', 'hierarchy']
    True
    >>> collect_links_wikitext(\
    "[[public transport|public transportation]][[kingdom (biology)|]][[Seattle, Washington|]]" + \
    "[[Wikipedia:Manual of Style (headings)|]]") == \
    ['public transport', 'kingdom (biology)',\
     'Seattle, Washington', 'Wikipedia:Manual of Style (headings)']
    True
    >>> collect_links_wikitext("[[public transport]]ation [[bus]]es, [[taxicab]]s, and [[tram]]s") \
    == ['public transport', 'bus', 'taxicab', 'tram']
    True
    >>> collect_links_wikitext("[[Wikipedia:Manual of Style#Italics]][[#Links and URLs]]" + \
    "[[#Links and URLs|Links and URLs]][[Wikipedia:Manual of Style#Italics|Italics]]") == \
    ['Wikipedia:Manual of Style', 'Wikipedia:Manual of Style']
    True
    """
    wikilinks = list()
    pattern = re.compile("\[\[[\S\s]*?\]\]")
    items = pattern.findall(wikitext)  # NOTE: Ignore style suggestions here.
    # items = re.findall("\[\[(.*?)\]\]", wikitext)
    # wikilinks = [_parse_wikilink(wikilink) or '' for wikilink in items]
    for wikilink in items:
        wikilinks += _parse_wikilink(wikilink[2:len(wikilink) - 2]) or ''

    return wikilinks


def _parse_wikilink(wikilink: str) -> list:
    """Return the linked article.

    Return None if links to section within page
    """
    try:
        # If the link is a section on the same page
        if wikilink[0] == "#":
            return []

        # TODO: Test if these micro-optimizations work properly (i.e. save any time)
        # If the link is a file or image
        if wikilink[0] == "F" \
                and wikilink[:5] == "File:" \
                or wikilink[0] == "I" \
                and wikilink[:6] == "Image:":
            pipe_index = wikilink.find("|")
            lsbr_index = wikilink.find("[[")
            if not (lsbr_index == -1 and pipe_index == -1):
                # TODO: Decide whether this needs to be fixed -- it works properly when called on by
                #  runner method large method so I don't think so
                # Maybe something is wrong -- ]] not being removed form this example:
                # _parse_wikilink('File:An écorché figure (life-size), lying prone on a table" +\
                # " Wellcome L0020561.jpg|thumb|A dissected body, lying prone on a table, by " +\
                # "[[Charles Landseer]]')
                # This works for some reason, but only when you run it on everything?
                # Not individually
                parsed_sublink = _parse_wikilink(wikilink[lsbr_index + 2:])
            else:
                parsed_sublink = wikilink

            return [wikilink if pipe_index == -1 else wikilink[:pipe_index]] +\
                (parsed_sublink if lsbr_index != -1 and parsed_sublink else [])

        # === If the link is... ===
        # ...a section on different page
        hash_index = wikilink.find("#")
        if hash_index != -1:
            pipe_index = wikilink.find("|")
            if pipe_index != -1 and pipe_index < hash_index:
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


def char_count(wikitext: str) -> int:
    """Return characters between <text> tags GIVEN <page> ELEMENT
    """
    text_start_index = wikitext.find("<text>")
    text_end_index = wikitext.find("</text>")
    return len(wikitext[text_start_index + 6:text_end_index])


def last_revision(wikitext: str) -> datetime:
    """Return last revision between <timestamp> tags GIVEN <page> ELEMENT
    """
    revision_start_index = wikitext.find("<timestamp>")
    revision_end_index = wikitext.find("</timestamp>")
    # minus one to remove Z
    return datetime.fromisoformat(wikitext[revision_start_index + 11:revision_end_index - 1])


if __name__ == "__main__":
    # cd to bruh/src so filepaths work no matter where they are
    os.chdir(__file__[0:-len('wikitext.py')])

    # Do doctest
    import doctest
    doctest.testmod()

    # Open testing files... options include k.xml, ninepointthreek.xml, hundredk.xml, million.xml
    with open('../data/raw/reduced/animation.xml', 'r') as reader:
        wikitext = reader.read()

    from experiments import versus_wtp

    print(last_revision(wikitext))

    # Code for comparing the time taken between wikitextparser and our solution
    # versus_wtp.time_versus("collect_links_wikitext(wikitext)",
    #                        "wtp.parse(wikitext)",
    #                        {"times": 2}, globals())

    # Code for comparing the output of wikitextparser and our solution
    # versus_wtp.diff_lists([item for item in collect_links_wikitext(wikitext) if item],
    #                       [l.title for l in wtp.parse(wikitext).wikilinks if l.title])