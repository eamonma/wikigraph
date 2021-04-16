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


def collect_links(wikitext: str) -> list:
    """Collect links given wikitext
    Find tags containing "[[]]" and parse within it.
    Maintains case.

    >>> collect_links(\
    "[[political philosophy]][[Political movement|movement]][[authority]][[hierarchy]]") == \
    ['political philosophy', 'Political movement', 'authority', 'hierarchy']
    True
    >>> collect_links(\
    "[[public transport|public transportation]][[kingdom (biology)|]][[Seattle, Washington|]]" + \
    "[[Wikipedia:Manual of Style (headings)|]]") == \
    ['public transport', 'kingdom (biology)',\
     'Seattle, Washington', 'Wikipedia:Manual of Style (headings)']
    True
    >>> collect_links("[[public transport]]ation [[bus]]es, [[taxicab]]s, and [[tram]]s") \
    == ['public transport', 'bus', 'taxicab', 'tram']
    True
    >>> collect_links("[[Wikipedia:Manual of Style#Italics]][[#Links and URLs]]" + \
    "[[#Links and URLs|Links and URLs]][[Wikipedia:Manual of Style#Italics|Italics]]") == \
    ['Wikipedia:Manual of Style', 'Wikipedia:Manual of Style']
    True
    """
    wikilinks = list()
    pattern = re.compile("\[\[[\S\s]*?\]\]")
    items = pattern.findall(wikitext)  # NOTE: Ignore style suggestions here.
    # items = re.findall("\[\[(.*?)\]\]", wikitext)
    # wikilinks = [parse_wikilink(wikilink) or '' for wikilink in items]
    for wikilink in items:
        wikilinks += parse_wikilink(wikilink[2:len(wikilink) - 2]) or ''

    return wikilinks


def parse_wikilink(wikilink: str) -> list:
    """Return the linked article.

    Return None if links to section within page
    """
    try:
        # If the link is a section on the same page
        if wikilink[0] == "#":
            return []

        # TODO: Test if these micro-optimizations work properly (i.e. save any time)
        # If the link is a file or image
        if wikilink[0] in {"f", "F"} \
                and wikilink[:5].lower() == "file:" \
                or wikilink[0] in {"i", "I"} \
                and wikilink[:6].lower() == "image:":
            pipe_index = wikilink.find("|")
            lsbr_index = wikilink.find("[[")
            if not (lsbr_index == -1 and pipe_index == -1):
                # TODO: Decide whether this needs to be fixed -- it works properly when called on by
                #  runner method large method so I don't think so
                # Maybe something is wrong -- ]] not being removed form this example:
                # parse_wikilink('File:An écorché figure (life-size), lying prone on a table" +\
                # " Wellcome L0020561.jpg|thumb|A dissected body, lying prone on a table, by " +\
                # "[[Charles Landseer]]')
                # This works for some reason, but only when you run it on everything?
                # Not individually
                parsed_sublink = parse_wikilink(wikilink[lsbr_index + 2:])
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


text_regex = re.compile("<text.*>")


def char_count(wikitext: str) -> int:
    """Return characters between <text> tags GIVEN <page> ELEMENT
    """
    text_start_tag_end_index = text_regex.search(wikitext).end()
    # ending tag is always 84 chars away from </page>| here
    return len(wikitext) - 84 - text_start_tag_end_index


def extract_content(wikitext: str) -> int:
    """Return content between <text> tags GIVEN <page> ELEMENT
    """
    text_start_tag_end_index = text_regex.search(wikitext).end()
    return wikitext[text_start_tag_end_index:len(wikitext) - 84]


def last_revision(wikitext: str) -> int:
    """Return last revision between <timestamp> tags GIVEN <page> ELEMENT
    """
    revision_start_index = wikitext.find("<timestamp>")
    revision_end_index = wikitext.find("</timestamp", revision_start_index)
    # time zone agnostic
    return (datetime.fromisoformat("2021-01-01T00:00:01+00:00").replace(tzinfo=None) -
            datetime.fromisoformat(
            wikitext[revision_start_index + 11:revision_end_index - 1].replace("Z", "+00:00")).replace(tzinfo=None)).seconds


def parse_redirect(wikitext: str) -> str:
    """Return empty string if page not redirect
    Return page to redirect
    """
    redirect_start_index = wikitext.find("<redirect")

    # if not redirect
    if redirect_start_index == -1:
        return ""

    # get index of immediate linebreak after
    redirect_end_index = wikitext.find("\n", redirect_start_index)
    # `<redirect title="` is 17 characters, `" />` is 4 characters
    return wikitext[redirect_start_index + 17: redirect_end_index - 4]


def get_title(wikitext: str) -> str:
    """Return title of <page>
    """
    # first <t of page is necessarily title
    title_start_index = wikitext.find("<title")
    # get index of immediate linebreak after
    title_end_index = wikitext.find("\n", title_start_index)
    # <title> is 7 characters, </title> is 8 characters
    return wikitext[title_start_index + 7: title_end_index - 8]


if __name__ == "__main__":
    # cd to bruh/src so filepaths work no matter where they are
    # os.chdir(__file__[0:-len('wikitext.py')])

    # Do doctest
    # import doctest
    # doctest.testmod()

    # Open testing files... options include k.xml, ninepointthreek.xml, hundredk.xml, million.xml
    with open('data/processed/partitioned/f.wk', 'r') as reader:
        wikitext = reader.read()

    from experiments import versus_wtp
    # print(collect_links(
    #     "file:Ceres and Vesta, Moon size comparison.jpg|thumb|The largest asteroid in the previous image, [[4 Vesta|Vesta"))

    # print((last_revision(wikitext) - datetime(2021, 1, 1)).seconds)

    # Code for comparing the time taken between wikitextparser and our solution
    # versus_wtp.time_versus("collect_links(wikitext)",
    #                        "wtp.parse(wikitext)",
    #                        {"times": 2}, globals())

    # Code for comparing the output of wikitextparser and our solution
    # versus_wtp.diff_lists([item for item in collect_links(wikitext) if item],
    #                       [l.title for l in wtp.parse(wikitext).wikilinks if l.title])
