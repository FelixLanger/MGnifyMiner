from mgyminer.constants import BIOMES
def get_hierarchy_levels(biome_strings):
    """
    Extracts and returns the unique hierarchical levels from a list of biome strings.

    This function processes a list of colon-separated hierarchical strings (biome strings)
    and extracts every possible hierarchical level within each string. Each unique level is
    collected and returned as a set, ensuring there are no duplicate entries across all
    biome strings.

    Parameters:
    - biome_strings (list of str): A list where each element is a string representing a
      hierarchical path in the format 'level1:level2:...:levelN'.

    Returns:
    - set: A set of unique strings, each representing a distinct hierarchical level extracted
      from the input list. The levels include every possible prefix of the input strings,
      ensuring that all hierarchical levels are captured.

    Example:
    >>> biome_strings = ['root:Host-associated:Mammals', 'root:Host-associated:Birds']
    >>> get_hierarchy_levels(biome_strings)
    {'root', 'root:Host-associated', 'root:Host-associated:Mammals', 'root:Host-associated:Birds'}
    """
    unique_biome_levels = set()

    for bio_str in biome_strings:
        parts = bio_str.split(":")
        for i in range(len(parts)):
            unique_biome_levels.add(':'.join(parts[:i + 1]))
    return unique_biome_levels


def available_biome_levels(unique_biome_ids):
    biomes = [BIOMES[i] for i in unique_biome_ids]
    return get_hierarchy_levels(biomes)