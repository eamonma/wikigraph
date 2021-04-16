"""Graph and _Vertex implementation for use in creating the Wikipedia graph"""
from __future__ import annotations
import os
import datetime
from typing import Any

# Make sure you've installed the necessary Python libraries (see assignment handout
# "Installing new libraries" section)
# Used for visualizing graphs (by convention, referred to as "nx")
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
    redirect: str

    # todo: temporarily set a default value
    def __init__(self, item: Any, char_count: int,
                 last_edit: int = 0, redirect: str = "") -> None:
        """Initialize a new vertex with the given item, char_count, last_edit,
        and redirect.

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

    # todo: determine usefulness of this with regards to answering our research question
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

    def add_vertex(self, item: Any, char_count: int, last_edit: int = 0,
                   redirect: str = "") -> None:
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

    def to_pyvis(self, max_vertices: int = 5000) -> Network:
        """Convert this graph into a PyVis Network object.

        max_vertices specifies the maximum number of vertices that can appear in the graph.

        TODO: NOTE THAT THIS DOES REQUIRE YOU TO HAVE PYVIS INSTALLED
        FIXME: every time you run this without iPython, you get a KeyError
        # https://towardsdatascience.com/making-network-graphs-interactive-with-python-and-pyvis-b754c22c270
        """
        graph_pyvis = Network()
        for v in self._vertices.values():
            graph_pyvis.add_node(v.item)

            for u in v.neighbours:
                if graph_pyvis.num_nodes() < max_vertices:
                    graph_pyvis.add_node(u.item)

                if u.item in graph_pyvis.nodes:
                    graph_pyvis.add_edge(v.item, u.item)

            if graph_pyvis.num_nodes() >= max_vertices:
                break

        return graph_pyvis

    # todo: determine usefulness
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
    """Return a graph corresponding to the save files."""


if __name__ == '__main__':
    # NOTE: Don't have these on all the time
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    os.chdir(__file__[0:-len('wikigraph/graph_implementation.py')])


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
