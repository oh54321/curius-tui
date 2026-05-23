import random

import pytest

from src.data_structures import (
    LinkedList,
    OrderStatisticRedBlackTree,
    RedBlackTree,
    TreeSet,
)


class TestLinkedList:
    def test_empty(self):
        ll = LinkedList[int]()
        assert len(ll) == 0
        assert list(ll) == []

    def test_append_and_iterate(self):
        ll = LinkedList[int]([1, 2, 3])
        assert len(ll) == 3
        assert list(ll) == [1, 2, 3]

    def test_remove_middle(self):
        ll = LinkedList[int]()
        a = ll.append(1)
        b = ll.append(2)
        c = ll.append(3)
        assert ll.remove(b) == 2
        assert list(ll) == [1, 3]
        assert ll.head is a
        assert ll.tail is c

    def test_remove_head_and_tail(self):
        ll = LinkedList[int]()
        a = ll.append(1)
        b = ll.append(2)
        ll.remove(a)
        assert list(ll) == [2]
        ll.remove(b)
        assert list(ll) == []
        assert ll.head is None
        assert ll.tail is None

    def test_clear(self):
        ll = LinkedList[int]([1, 2, 3])
        ll.clear()
        assert len(ll) == 0
        assert list(ll) == []


class TestRedBlackTree:
    def test_inorder_is_sorted(self):
        values = [7, 3, 9, 1, 5, 8, 2, 4, 6]
        tree = RedBlackTree[int](values)
        assert list(tree) == sorted(values)

    def test_contains(self):
        tree = RedBlackTree[int]([1, 2, 3])
        assert 2 in tree
        assert 99 not in tree

    def test_min_max(self):
        tree = RedBlackTree[int]([5, 1, 3, 9, 2])
        assert tree.min() == 1
        assert tree.max() == 9

    def test_insert_duplicate_returns_false(self):
        tree = RedBlackTree[int]()
        assert tree.insert(1) is True
        assert tree.insert(1) is False
        assert len(tree) == 1

    def test_remove(self):
        tree = RedBlackTree[int]([1, 2, 3, 4, 5])
        tree.remove(3)
        assert list(tree) == [1, 2, 4, 5]
        assert 3 not in tree

    def test_random_stress(self):
        rng = random.Random(0xC471)
        values = rng.sample(range(1000), 200)
        tree = RedBlackTree[int](values)
        assert list(tree) == sorted(values)
        for v in values[:50]:
            tree.remove(v)
        remaining = sorted(values[50:])
        assert list(tree) == remaining


class TestTreeSet:
    def test_add_discard(self):
        ts = TreeSet[int]([1, 2, 3])
        assert 2 in ts
        ts.discard(2)
        assert 2 not in ts
        assert len(ts) == 2

    def test_first_last(self):
        ts = TreeSet[int]([3, 1, 2])
        assert ts.first() == 1
        assert ts.last() == 3


class TestOrderStatisticRBT:
    def test_select_by_rank(self):
        tree = OrderStatisticRedBlackTree[int]()
        for v in [5, 1, 4, 2, 3]:
            tree.insert(v)
        assert [tree.select(i) for i in range(5)] == [1, 2, 3, 4, 5]

    def test_count_range(self):
        tree = OrderStatisticRedBlackTree[int]()
        for v in range(1, 11):  # 1..10
            tree.insert(v)
        assert tree.count_range(3, 7) == 5
        assert tree.count_range(1, 10) == 10
        assert tree.count_range(50, 100) == 0

    def test_remove_by_rank(self):
        tree = OrderStatisticRedBlackTree[int]()
        for v in [10, 20, 30, 40]:
            tree.insert(v)
        tree.remove_by_rank(0)  # remove 10
        assert tree.select(0) == 20
        assert len(tree) == 3

    def test_select_out_of_range_raises(self):
        tree = OrderStatisticRedBlackTree[int]([1, 2, 3])
        with pytest.raises((IndexError, ValueError)):
            tree.select(99)

    def test_random_stress_matches_sorted_list(self):
        rng = random.Random(0xFEED)
        values = rng.sample(range(10_000), 500)
        tree = OrderStatisticRedBlackTree[int]()
        for v in values:
            tree.insert(v)
        sorted_values = sorted(values)
        for _ in range(100):
            i = rng.randrange(len(sorted_values))
            assert tree.select(i) == sorted_values[i]
