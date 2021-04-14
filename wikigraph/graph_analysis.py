#!/usr/bin/env python3
"""Functions for analysing the graph of Wikipedia data."""
from __future__ import annotations
import os
from typing import Any, Optional
from graph_implementation import Graph


def find_fewest_edges_threshold(g: Graph, threshold: int, cap: Optional[int] = None) -> set:
    """Return the set of vertices with fewer than or equal to threshold edges.
    If cap is given, return only the first cap items below the threshold. If there are
    fewer than cap items with a degree below the threshold, fewer than cap items will
    be returned.

    Preconditions:
        - 0 <= threshold
        - cap is None or 0 <= cap <= len(self._vertices)

    >>> g = Graph()
    >>> g.add_vertex('first', word_count=20)  # placeholder word_count
    >>> g.add_vertex('second', word_count=20)
    >>> g.add_vertex('third', word_count=20)
    >>> g.add_vertex('fourth', word_count=20)
    >>> g.add_vertex('fifth', word_count=20)
    >>> g.add_edge('first', 'second')
    >>> g.add_edge('first', 'third')
    >>> g.add_edge('first', 'fourth')
    >>> g.add_edge('first', 'fifth')
    >>> g.add_edge('third', 'fifth')
    >>> g.add_edge('fourth', 'fifth')
    >>> s = find_fewest_edges_threshold(g, 2)
    >>> s == {'second', 'third', 'fourth'}
    True
    """
    # the vertices, sorted by degree; contains vertex *items*
    lst = list(g.get_all_vertices())
    sorted_lst = _sort_vertices_by_degree(g, lst)
    few_edges = set()

    for i in range(len(sorted_lst)):
        if cap is not None and cap <= 0:
            return few_edges

        item = sorted_lst[i]
        if g.get_vertex_degree(item) <= threshold and cap is None:
            few_edges.add(item)
        elif g.get_vertex_degree(item) <= threshold and cap > 0:
            few_edges.add(item)
            cap = cap - 1

    return few_edges


def find_fewest_edges_no_threshold(g: Graph, cap: int) -> list:
    """Return a list of cap vertices with the smallest degrees in the graph. If there are
    fewer than cap items with a degree below the threshold, fewer than cap items will
    be returned.

    Preconditions:
        - 0 <= cap <= len(g.get_all_vertices())

    >>> g = Graph()
    >>> g.add_vertex('first', word_count=20) # placeholder for word_count
    >>> g.add_vertex('second', word_count=20)
    >>> g.add_vertex('third', word_count=20)
    >>> g.add_vertex('fourth', word_count=20)
    >>> g.add_vertex('fifth', word_count=20)
    >>> g.add_edge('first', 'second')
    >>> g.add_edge('first', 'third')
    >>> g.add_edge('first', 'fourth')
    >>> g.add_edge('first', 'fifth')
    >>> g.add_edge('third', 'fifth')
    >>> g.add_edge('fourth', 'fifth')
    >>> lst = find_fewest_edges_no_threshold(g, 3)
    >>> lst
    >>> lst == ['second', 'third', 'fourth'] or lst == ['second', 'fourth', 'third']
    True
    """
    # the vertices, sorted by degree; contains vertex *items*
    lst = list(g.get_all_vertices())
    sorted_few = _cap_smallest_degrees(g, lst, cap)
    return sorted_few


def _cap_smallest_degrees(g: Graph, lst: list, cap: int) -> list:
    """Return sorted list of first cap items with the smallest degrees.

    Preconditions:
        - 0 <= cap <= len(lst)
        - No duplicates in lst
    """
    if len(lst) < 2:
        return lst.copy()
    else:
        pivot = g.get_vertex_degree(lst[0])
        smaller, bigger = _partition_by_degree(g, lst[1:], pivot)

        if len(lst) == cap:
            # if length of list is cap, just return the sorted list
            smaller_sorted = _cap_smallest_degrees(g, smaller, len(smaller))
            bigger_sorted = _cap_smallest_degrees(g, bigger, len(bigger))

            return smaller_sorted + [lst[0]] + bigger_sorted

        elif len(smaller) == cap - 1:
            smaller_sorted = _sort_vertices_by_degree(g, smaller)
            return smaller_sorted + [lst[0]]

        elif len(smaller) < cap:
            # must recurse on both smaller and bigger
            smaller_sorted = _cap_smallest_degrees(g, smaller, len(smaller))
            bigger_sorted = _cap_smallest_degrees(g, bigger, cap - len(smaller) - 1)

            return smaller_sorted + [lst[0]] + bigger_sorted

        else:  # if len(smaller) > cap
            return _cap_smallest_degrees(g, smaller, cap)


def _sort_vertices_by_degree(g: Graph, lst: list) -> list:
    """Return a list of the vertices contained in lst, sorted from lowest
    to highest degree.

    Precondition:
        - all(lst[i] for i in range(len(lst)))
    """
    if len(lst) < 2:
        return lst.copy()
    else:
        pivot = g.get_vertex_degree(lst[0])

        smaller, bigger = _partition_by_degree(g, lst[1:], pivot)

        sorted_smaller = _sort_vertices_by_degree(g, smaller)
        sorted_bigger = _sort_vertices_by_degree(g, bigger)

        # returning a list of ITEMS
        return sorted_smaller + [lst[0]] + sorted_bigger


def _partition_by_degree(g: Graph, lst: list, pivot: Any) -> tuple[list, list]:
    """Return a partition of lst with the chosen pivot.

    Return two lists, where the first contains the items in lst whose degrees are
    <= pivot, and the second contains the items in lst with degrees > pivot.
    """
    smaller = []
    bigger = []

    for item in lst:
        if g.get_vertex_degree(item) <= pivot:
            smaller.append(item)
        else:
            bigger.append(item)

    return (smaller, bigger)


if __name__ == '__main__':
    # NOTE: Don't have these on all the time
    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    os.chdir(__file__[0:-len('graph_analysis.py')])

    # NOTE: These others are fine
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'max-line-length': 1000,
        'disable': ['E1136'],
        'extra-imports': ['csv', 'networkx'],
        'allowed-io': ['load_review_graph'],
        'max-nested-blocks': 4
    })