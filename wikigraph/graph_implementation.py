"""Graph and _Vertex implementation for use in creating the Wikipedia graph"""
from __future__ import annotations

import fileinput
import os
import datetime
from tqdm import tqdm
from typing import Any
import math

# Make sure you've installed the necessary Python libraries (see assignment handout
# "Installing new libraries" section)
# Used for visualizing graphs (by convention, referred to as "nx")
from pyvis.network import Network
import networkx as nx


class _Vertex:
    """A vertex in a graph representing Wikipedia. Each vertex item is an article in Wikipedia,
    with edges representing internal links in Wikipedia between articles.

    Instance Attributes:
        - item: The data stored in this vertex, representing a Wikipedia article.
        - neighbours: The vertices that are adjacent to this vertex.
        - char_count: The character count of the article
        - last_edit: Time since the date of last revision and January 1st, 2021, the day
                     the data was collected

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    item: Any
    neighbours: set[_Vertex]
    char_count: int
    last_edit: int
    score: float

    def __init__(self, item: Any, char_count: int, last_edit: int = 0) -> None:
        """Initialize a new vertex with the given item, char_count, and last_edit.

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.neighbours = set()
        self.char_count = char_count
        self.last_edit = last_edit

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    def set_score(self) -> int:
        """Compute and store score:

        higher char count = higher score,
        lower last_edit = higher score,
        more neigbours = higher score,
        """
        self.score = (self.char_count * len(self.neighbours)) / math.log(self.last_edit + 1)


class Graph:
    """A graph used to represent the Wikipedia article network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, char_count: int, last_edit: int = 0) -> None:
        """Add a vertex with the given item and char_count to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, char_count, last_edit)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            pass

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self) -> set:
        """Return a set of all vertex items in this graph.
        """
        return set(self._vertices.keys())

    def get_vertex_degree(self, item: Any) -> int:
        """Return the degree of the vertex associated with item.

        Raise a ValueError if item does not appear as a vertex in this graph."""
        if item in self._vertices:
            return len(self._vertices[item].neighbours)
        else:
            raise ValueError

    def get_vertex_char_count(self, item: Any) -> int:
        """Return the character count of the vertex associated with item.

        Raise a ValueError if item does not appear as a vertex in this graph."""
        if item in self._vertices:
            return self._vertices[item].char_count
        else:
            raise ValueError

    def get_vertex_edit_time(self, item: Any) -> int:
        """Return the last_edit of item.

        Raise a ValueError if item does not appear as a vertex in this graph."""
        if item in self._vertices:
            return self._vertices[item].last_edit
        else:
            raise ValueError

    def get_vertex_score(self, item: Any) -> int:
        """Return the score of the vertex associated with item.

        Raise a ValueError if item does not appear as a vertex in this graph."""
        if item in self._vertices:
            return self._vertices[item].score
        else:
            raise ValueError

    def to_pyvis(self, max_vertices: int = 5000) -> Network:
        """Convert this graph into a PyVis Network object.

        max_vertices specifies the maximum number of vertices that can appear in the graph.

        NOTE: Running this method withough iPython may result in KeyErrors
        """
        graph_pyvis = Network()
        for v in self._vertices.values():
            graph_pyvis.add_node(v.item)

            for u in v.neighbours:
                if graph_pyvis.num_nodes() < max_vertices:
                    graph_pyvis.add_node(u.item)

                if u.item in graph_pyvis.get_nodes():
                    graph_pyvis.add_edge(v.item, u.item)

            if graph_pyvis.num_nodes() >= max_vertices:
                break

        return graph_pyvis


def load_graph(info_file: str, links_file: str) -> Graph:
    """Return a graph corresponding to the save files."""
    graph = Graph()

    # Read file line by line for ram management
    for line in tqdm(fileinput.input([info_file])):
        row = line.split('\t')
        graph.add_vertex(row[0], row[1], row[2])

    for line in tqdm(fileinput.input([links_file])):
        row = line.split('\t')
        item1 = row[0]
        for item2 in row[1:]:
            graph.add_edge(item1, item2)

    return graph


if __name__ == '__main__':

    # NOTE: Don't have these on all the time
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    os.chdir(__file__[0:-len('wikigraph/graph_implementation.py')])

    g = load_graph('data/processed/graph/wiki-info-collapsed.tsv',
                   'data/processed/graph/wiki-links-collapsed.tsv')

    from wikigraph.graph_analysis import analysis
    analysis(g, 100)

    # # NOTE: These others are fine
    # import doctest
    # doctest.testmod()

    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 1000,
    #     'disable': ['E1136'],
    #     'extra-imports': ['csv', 'networkx'],
    #     'allowed-io': ['load_review_graph'],
    #     'max-nested-blocks': 4
    # })
