#!/usr/bin/env python3
"""Graph and _Vertex implementation for use in creating the Wikipedia graph"""
from __future__ import annotations
import os
import datetime
from typing import Any

# Make sure you've installed the necessary Python libraries (see assignment handout
# "Installing new libraries" section)
import networkx as nx  # Used for visualizing graphs (by convention, referred to as "nx")


class _Vertex:
    """A vertex in a book review graph, used to represent a user or a book.

    Each vertex item is either a user id or book title. Both are represented as strings,
    even though we've kept the type annotation as Any to be consistent with lecture.

    Instance Attributes:
        - item: The data stored in this vertex, representing a user or book.
        - kind: The type of this vertex: 'user' or 'book'.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'user', 'book'}
    """
    item: Any
    neighbours: set[_Vertex]
    char_count: int
    last_edit: datetime.timedelta
    redirect: str

    def __init__(self, item: Any, char_count: int,
                 last_edit: datetime.timedelta, redirect: str = "") -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.neighbours = set()
        self.redirect = redirect
        self.char_count = char_count
        self.last_edit = last_edit

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)

    # NOTE: This might be useful some time in the future so I'm leaving it here
    # def similarity_score(self, other: _Vertex) -> float:
    #     """Return the similarity score between this vertex and other.

    #     See Assignment handout for definition of similarity score.
    #     """
    #     if not self.degree() or not other.degree():
    #         return 0

    #     top = len(self.neighbours.intersection(other.neighbours))
    #     bottom = len(self.neighbours.union(other.neighbours))

    #     return top / bottom


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

    def add_vertex(self, item: Any, word_count: int) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'user', 'book'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, word_count)

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
            raise ValueError

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

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'user', 'book'}
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
        """Return the word count of the vertex associated with item.

        Raise a ValueError if item does not appear as a vertex in this graph."""
        if item in self._vertices:
            return self._vertices[item].word_count
        else:
            raise ValueError

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        Note that this method is provided for you, and you shouldn't change it.
        """
        graph_nx = nx.Graph()
        for v in self._vertices.values():
            graph_nx.add_node(v.item, kind=v.kind)

            for u in v.neighbours:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.item, kind=u.kind)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx

    # NOTE: This might be useful some time in the future so I'm leaving it here
    # def get_similarity_score(self, item1: Any, item2: Any) -> float:
    #     """Return the similarity score between the two given items in this graph.

    #     Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

    #     >>> g = Graph()
    #     >>> for i in range(0, 6):
    #     ...     g.add_vertex(str(i), kind='user')
    #     >>> g.add_edge('0', '2')
    #     >>> g.add_edge('0', '3')
    #     >>> g.add_edge('0', '4')
    #     >>> g.add_edge('1', '3')
    #     >>> g.add_edge('1', '4')
    #     >>> g.add_edge('1', '5')
    #     >>> g.get_similarity_score('0', '1')
    #     0.5
    #     """
    #     if item1 not in self._vertices or item2 not in self._vertices:
    #         raise ValueError

    #     return self._vertices[item1].similarity_score(self._vertices[item2])


def load_graph(edges_file: str, characteristics_file: str) -> Graph:
    """Return a graph coresponding to the save files."""


if __name__ == '__main__':
    # NOTE: Don't have these on all the time
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    os.chdir(__file__[0:-len('graph_implementation.py')])

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
