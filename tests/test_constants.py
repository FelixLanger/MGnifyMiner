import pytest

from mgyminer.constants import BiomeMatrix

biomes = {
    0: "root",
    1: "root:A",
    2: "root:A:B",
    3: "root:A:B:C",
    4: "root:A:B:D",
    5: "root:A:E",
    6: "root:F",
    7: "root:F:G",
    8: "root:F:H",
    9: "root:F:H:I",
}


@pytest.fixture
def biome_matrix():
    return BiomeMatrix(biomes)


def test_get_children(biome_matrix):
    assert biome_matrix.get_children(0) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert biome_matrix.get_children(1) == [2, 3, 4, 5]
    assert biome_matrix.get_children(2) == [3, 4]
    assert biome_matrix.get_children(6) == [7, 8, 9]
    assert biome_matrix.get_children(8) == [9]
    assert biome_matrix.get_children(9) == []


def test_get_parents(biome_matrix):
    assert biome_matrix.get_parents(0) == []
    assert biome_matrix.get_parents(1) == [0]
    assert biome_matrix.get_parents(2) == [0, 1]
    assert biome_matrix.get_parents(3) == [0, 1, 2]
    assert biome_matrix.get_parents(8) == [0, 6]
    assert biome_matrix.get_parents(9) == [0, 6, 8]


def test_get_unique_children(biome_matrix):
    assert biome_matrix.get_unique_children([1, 6]) == {2, 3, 4, 5, 7, 8, 9}
    assert biome_matrix.get_unique_children([2, 7]) == {3, 4}
    assert biome_matrix.get_unique_children([3, 5, 8]) == {9}
    assert biome_matrix.get_unique_children([4, 9]) == set()
    assert biome_matrix.get_unique_children([0]) == {1, 2, 3, 4, 5, 6, 7, 8, 9}
    assert biome_matrix.get_unique_children([]) == set()


def test_get_unique_parents(biome_matrix):
    assert biome_matrix.get_unique_parents([2, 7]) == {0, 1, 6}
    assert biome_matrix.get_unique_parents([3, 5, 8]) == {0, 1, 2, 6}
    assert biome_matrix.get_unique_parents([4, 9]) == {0, 1, 2, 6, 8}
    assert biome_matrix.get_unique_parents([0]) == set()
    assert biome_matrix.get_unique_parents([1, 6]) == {0}
    assert biome_matrix.get_unique_parents([]) == set()
