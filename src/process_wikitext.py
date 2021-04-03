#!/usr/bin/env python3
"""Process the wikitext and save two graph save files in data/processed

Edge save format:
- Option 1: Python dictionary that can just be loaded in
=================
dictionary = {
    vertex1: {edges1},
    vertex2: {edges2},
    vertex2: {edges3}
}
=================
- Option 2: CSV that we can load in
=================
vertex1,edge1-1,edge1-2,...
vertex2,edge2-1,edge2-2,...
vertex3,edge3-1,edge3-2,...
=================

Information/Metrics save format:
=================
vertex1,wordcount1,otherthings1
vertex2,wordcount2,otherthings2
vertex3,wordcount3,otherthings3
=================
"""
import os

# FIXME: This doesn't work, look for large files specifically
def read_n_lines(data_file: str, start_line: int, end_line: int) -> str:
    """Read from start_line to end_line from the data file and return it
    (return type pending, something like an list of strings might be better suited?)
    """
    output = ""
    f = open(data_file)
    lines_to_read = [start_line, end_line]

    for position, line in enumerate(f):
        if position in lines_to_read:
            output += line

    return output

# Some notes first:
# - We should probably lower case everything that we check the link to or find
#   whatever because then we don't
# - Find a way to read in a smaller number of lines than the entire file...
#   none of us have 80 gigs of ram
# - look for <page> and then <title>Title</title>
# - If we find <redirect title="Some Other Title" />, then mark as a redirect
#   - If we find someone linking to this, then we just link to whatever it redirects to
#   - Add an instance attribute that is an empty string if not a redirect,
#     and is the name of the redirect title if it is a redirect (Maybe the vertex
#     directly so we don't have to search)

if __name__ == '__main__':
    os.chdir(__file__[0:-19])
    print(read_n_lines('../data/raw/enwiki-20210101-pages-articles-multistream.xml', 0, 10))
