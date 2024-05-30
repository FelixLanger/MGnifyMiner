from mgyminer.plots.tree import plot_tree
from mgyminer.proteintable import ProteinTable
from tests.helpers import calculate_md5


def test_simple_plot_tree(tmp_path, tree):
    tree_image = tmp_path / "test_tree.jpg"
    fig = plot_tree(tree)
    fig.write_image(tree_image)
    assert calculate_md5(tree_image) == "aad98fdbbe7ba3b6f8a851565e7f613a"


def test_plot_tree_with_domains(tmp_path, tree, results_metadata):
    tree_image = tmp_path / "test_tree.jpg"
    pt = ProteinTable(results_metadata)
    arch_data = pt[["target_name", "pfam_architecture"]].copy()
    fig = plot_tree(tree, arch_data)
    fig.write_image(tree_image)
    assert calculate_md5(tree_image) == "4446103aec096b1e191982908a21b5f6"


def test_plot_tree_custom_nodes(tmp_path, tree, results_metadata):
    tree_image = tmp_path / "test_tree.jpg"
    pt = ProteinTable(results_metadata)
    arch_data = pt[["target_name", "pfam_architecture"]].copy()
    fig = plot_tree(
        tree,
        arch_data,
        node_colors={"MGYP001046131171": "green"},
    )
    fig.write_image(tree_image)
    assert calculate_md5(tree_image) == "c42881d604bccce60a2e2858ab2e24bb"


def test_plot_tree_custom_domain_col(tmp_path, tree, results_metadata):
    tree_image = tmp_path / "test_tree.jpg"
    pt = ProteinTable(results_metadata)
    arch_data = pt[["target_name", "pfam_architecture"]].copy()
    fig = plot_tree(tree, arch_data, domain_colors={"PF01752": "black"})
    fig.write_image(tree_image)
    assert calculate_md5(tree_image) == "b3a7c46339a6cd6bab327b6f32fd27c6"
