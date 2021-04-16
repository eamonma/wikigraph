"""Functions for analysing the graph of Wikipedia data."""
from __future__ import annotations
import os
from typing import Any, Optional
from graph_implementation import Graph


#################################################################################
# Last Edit Analysis
#################################################################################
def find_oldest_edits(g: Graph, n: int) -> list:
    """Return a list of n vertices whose associated articles have the longest
    time since last edit.

    Preconditions:
        - 0 <= n <= len(g.get_all_vertices())

    >>> g = Graph()
    >>> g.add_vertex('first', char_count=1, last_edit=111)
    >>> g.add_vertex('second', char_count=2, last_edit=32)
    >>> g.add_vertex('third', char_count=3, last_edit=38)
    >>> g.add_vertex('fourth', char_count=4, last_edit=411)
    >>> g.add_vertex('fifth', char_count=5, last_edit=50)
    >>> g.add_edge('first', 'second')
    >>> g.add_edge('first', 'third')
    >>> g.add_edge('fourth', 'fifth')
    >>> l = find_oldest_edits(g, 3)
    >>> l
    ['fifth', 'first', 'fourth']
    """
    lst = list(g.get_all_vertices())
    sorted_oldest = _n_oldest_edits(g, lst, n)
    return sorted_oldest


def _n_oldest_edits(g: Graph, lst: list, n: int) -> list:
    """Return a list of n vertices in lst whose associated articles have the
    longest time since last edit.

    Preconditions:
        - lst contains no duplicates
        - 0 <= n <= len(g.get_all_vertices())
    """
    if len(lst) < 2:
        return lst.copy()
    else:
        pivot = g.get_vertex_edit_time(lst[0])
        smaller, bigger = _partition_last_edit(g, lst[1:], pivot)

        if len(lst) == n:
            # if length of list is n, just return the sorted list
            smaller_sorted = _n_oldest_edits(g, smaller, len(smaller))
            bigger_sorted = _n_oldest_edits(g, bigger, len(bigger))

            return smaller_sorted + [lst[0]] + bigger_sorted

        elif len(bigger) == n - 1:
            bigger_sorted = _sort_vertices_last_edit(g, bigger)
            return [lst[0]] + bigger_sorted

        elif len(bigger) < n:
            # must recurse on both smaller and bigger
            smaller_sorted = _n_oldest_edits(g, smaller, n - len(bigger) - 1)
            bigger_sorted = _n_oldest_edits(g, bigger, len(bigger))

            return smaller_sorted + [lst[0]] + bigger_sorted

        else:  # if len(bigger) > n
            return _n_oldest_edits(g, bigger, n)


def _sort_vertices_last_edit(g: Graph, lst: list) -> list:
    """Return a list of all the vertices contained in lst, sorted from
    shortest time since last edit to longest time since last edit.
    """
    if len(lst) < 2:
        return lst.copy()
    else:
        pivot = g.get_vertex_edit_time(lst[0])

        smaller, bigger = _partition_last_edit(g, lst[1:], pivot)

        sorted_smaller = _sort_vertices_last_edit(g, smaller)
        sorted_bigger = _sort_vertices_last_edit(g, bigger)

        # returning a list of ITEMS
        return sorted_smaller + [lst[0]] + sorted_bigger


def _partition_last_edit(g: Graph, lst: list, pivot: Any) -> tuple[list, list]:
    """Return a partition of lst with the chosen pivot.

    Return two lists, where the first contains the items in lst whose last edits are
    <= pivot, and the second contains the items in lst with last_edit > pivot.
    """
    smaller = []
    bigger = []

    for item in lst:
        if g.get_vertex_edit_time(item) <= pivot:
            smaller.append(item)
        else:
            bigger.append(item)

    return (smaller, bigger)


#################################################################################
# Character Count Analysis
#################################################################################
def find_smallest_char_counts(g: Graph, n: int) -> list:
    """Return a list of n vertices whose associated articles have the smallest character
    counts.

    Preconditions:
        - 0 <= n <= len(g.get_all_vertices())

    >>> g = Graph()
    >>> g.add_vertex('first', 100)
    >>> g.add_vertex('second', 100)
    >>> g.add_vertex('third', 30)
    >>> g.add_vertex('fourth', 400)
    >>> g.add_vertex('fifth', 500)
    >>> g.add_edge('first', 'second')
    >>> g.add_edge('first', 'third')
    >>> g.add_edge('fourth', 'fifth')
    >>> l = find_smallest_char_counts(g, 3)
    >>> l == ['third', 'first', 'second'] or l == ['third', 'second', 'first']
    True
    """
    lst = list(g.get_all_vertices())
    sorted_small = _n_smallest_chars(g, lst, n)
    return sorted_small


def _n_smallest_chars(g: Graph, lst: list, n: int) -> list:
    """Return a list of n vertices in lst whose associated articles have the
    smallest character counts.

    Preconditions:
        - lst contains no duplicates
        - 0 <= n <= len(g.get_all_vertices())
    """
    if len(lst) < 2:
        return lst.copy()
    else:
        pivot = g.get_vertex_char_count(lst[0])
        smaller, bigger = _partition_char_count(g, lst[1:], pivot)

        if len(lst) == n:
            # if length of list is n, just return the sorted list
            smaller_sorted = _n_smallest_chars(g, smaller, len(smaller))
            bigger_sorted = _n_smallest_chars(g, bigger, len(bigger))

            return smaller_sorted + [lst[0]] + bigger_sorted

        elif len(smaller) == n - 1:
            smaller_sorted = _sort_vertices_char_count(g, smaller)
            return smaller_sorted + [lst[0]]

        elif len(smaller) < n:
            # must recurse on both smaller and bigger
            smaller_sorted = _n_smallest_chars(g, smaller, len(smaller))
            bigger_sorted = _n_smallest_chars(g, bigger, n - len(smaller) - 1)

            return smaller_sorted + [lst[0]] + bigger_sorted

        else:  # if len(smaller) > n
            return _n_smallest_chars(g, smaller, n)


def _sort_vertices_char_count(g: Graph, lst: list) -> list:
    """Return a list of the vertices contained in lst, sorted from lowest
    to highest character counts.

    Preconditions:
        - all(lst[i] for i in range(len(lst)))
    """
    if len(lst) < 2:
        return lst.copy()
    else:
        pivot = g.get_vertex_char_count(lst[0])

        smaller, bigger = _partition_char_count(g, lst[1:], pivot)

        sorted_smaller = _sort_vertices_char_count(g, smaller)
        sorted_bigger = _sort_vertices_char_count(g, bigger)

        # returning a list of ITEMS
        return sorted_smaller + [lst[0]] + sorted_bigger


def _partition_char_count(g: Graph, lst: list, pivot: Any) -> tuple[list, list]:
    """Return a partition of lst with the chosen pivot.

    Return two lists, where the first contains the items in lst whose chararcter
    counts are <= pivot, and the second contains the items in lst with character
    counts > pivot.
    """
    smaller = []
    bigger = []

    for item in lst:
        if g.get_vertex_char_count(item) <= pivot:
            smaller.append(item)
        else:
            bigger.append(item)

    return (smaller, bigger)


#################################################################################
# Link Count Analysis
#################################################################################
def find_fewest_edges_threshold(g: Graph, threshold: int, n: Optional[int] = None) -> set:
    """Return the set of vertices with fewer than or equal to threshold edges.
    If n is given, return only the first n items below the threshold. If there are
    fewer than n items with a degree below the threshold, fewer than n items will
    be returned.

    Preconditions:
        - 0 <= threshold
        - n is None or 0 <= n <= len(g.get_all_vertices())

    >>> g = Graph()
    >>> g.add_vertex('first', char_count=20)  # placeholder char_count
    >>> g.add_vertex('second', char_count=20)
    >>> g.add_vertex('third', char_count=20)
    >>> g.add_vertex('fourth', char_count=20)
    >>> g.add_vertex('fifth', char_count=20)
    >>> g.add_edge('first', 'second')
    >>> g.add_edge('first', 'third')
    >>> g.add_edge('first', 'fourth')
    >>> g.add_edge('first', 'fifth')
    >>> g.add_edge('third', 'fifth')
    >>> g.add_edge('fourth', 'fifth')
    >>> s = find_fewest_edges_threshold(g, 2)
    >>> s == {'second', 'third', 'fourth'}
    True
    >>> s1 = find_fewest_edges_threshold(g, 1, 3)
    >>> s1 == {'second'}
    True
    """
    # the vertices, sorted by degree; contains vertex *items*
    lst = list(g.get_all_vertices())
    sorted_lst = _sort_vertices_by_degree(g, lst)
    few_edges = set()

    for i in range(len(sorted_lst)):
        if n is not None and n <= 0:
            return few_edges

        item = sorted_lst[i]
        if g.get_vertex_degree(item) <= threshold and n is None:
            few_edges.add(item)
        elif n is not None and g.get_vertex_degree(item) <= threshold:
            if n > 0:
                few_edges.add(item)
                n = n - 1

    return few_edges


def find_fewest_edges_no_threshold(g: Graph, n: int) -> list:
    """Return a list of n vertices with the smallest degrees in the graph.

    Preconditions:
        - 0 <= n <= len(g.get_all_vertices())

    >>> g = Graph()
    >>> g.add_vertex('first', char_count=20) # placeholder for char_count
    >>> g.add_vertex('second', char_count=20)
    >>> g.add_vertex('third', char_count=20)
    >>> g.add_vertex('fourth', char_count=20)
    >>> g.add_vertex('fifth', char_count=20)
    >>> g.add_edge('first', 'second')
    >>> g.add_edge('first', 'third')
    >>> g.add_edge('first', 'fourth')
    >>> g.add_edge('first', 'fifth')
    >>> g.add_edge('third', 'fifth')
    >>> g.add_edge('fourth', 'fifth')
    >>> lst = find_fewest_edges_no_threshold(g, 3)
    >>> lst == ['second', 'third', 'fourth'] or lst == ['second', 'fourth', 'third']
    True
    """
    # the vertices, sorted by degree; contains vertex *items*
    lst = list(g.get_all_vertices())
    sorted_few = _n_smallest_degrees(g, lst, n)
    return sorted_few


def _n_smallest_degrees(g: Graph, lst: list, n: int) -> list:
    """Return sorted list of first n items with the smallest degrees.

    Preconditions:
        - 0 <= n <= len(lst)
        - No duplicates in lst
    """
    if len(lst) < 2:
        return lst.copy()
    else:
        pivot = g.get_vertex_degree(lst[0])
        smaller, bigger = _partition_by_degree(g, lst[1:], pivot)

        if len(lst) == n:
            # if length of list is n, just return the sorted list
            smaller_sorted = _n_smallest_degrees(g, smaller, len(smaller))
            bigger_sorted = _n_smallest_degrees(g, bigger, len(bigger))

            return smaller_sorted + [lst[0]] + bigger_sorted

        elif len(smaller) == n - 1:
            smaller_sorted = _sort_vertices_by_degree(g, smaller)
            return smaller_sorted + [lst[0]]

        elif len(smaller) < n:
            # must recurse on both smaller and bigger
            smaller_sorted = _n_smallest_degrees(g, smaller, len(smaller))
            bigger_sorted = _n_smallest_degrees(g, bigger, n - len(smaller) - 1)

            return smaller_sorted + [lst[0]] + bigger_sorted

        else:  # if len(smaller) > n
            return _n_smallest_degrees(g, smaller, n)


def _sort_vertices_by_degree(g: Graph, lst: list) -> list:
    """Return a list of the vertices contained in lst, sorted from lowest
    to highest degree.

    Preconditions:
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
        'extra-imports': ['csv', 'networkx', 'os', 'graph_implementation'],
        'allowed-io': ['load_review_graph'],
        'max-nested-blocks': 4
    })
