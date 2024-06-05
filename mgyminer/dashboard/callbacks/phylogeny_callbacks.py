from Bio.Align import MultipleSeqAlignment
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from dash import Input, Output, State, callback
from pyfamsa import Aligner, Sequence
from pyfastx import Fasta

from mgyminer.dashboard.utils.data_store import protein_store
from mgyminer.plots.tree import plot_tree

# path = "/home/flx/PycharmProjects/multiminer/MultiMiner/prototyping/PA/mgnifyminer_results/hits.fa"
path = "/home/flx/PycharmProjects/MGnifyMiner2/results/roxp_hits.fa"
fasta = Fasta(path)


@callback(
    Output("additional-scatter", "figure"),
    Input("create-tree-btn", "n_clicks"),
    State("show-domains-switch", "value"),
    State("results-scatter", "selectedData"),
)
def update_phylogenetic_tree(n_clicks, show_domains, selected_data):
    if n_clicks is None or selected_data is None:
        return {}

    # Get the selected point IDs from the hovered data
    selected_ids = [point["pointIndex"] for point in selected_data["points"]]
    # Slice the dataframe to only contain metadata about the selected points
    pt = protein_store.get_dataframe()
    selected_dataframe = pt.loc[selected_ids]
    # Get the relevant sequences from the fasta object
    sequences = []
    for _, row in selected_dataframe.iterrows():
        sequence_id = row["target_name"]
        start = row["env_from"]
        stop = row["env_to"]

        sequence = fasta[sequence_id]
        subsequence = sequence[start - 1 : stop]
        sequences.append(Sequence(subsequence.name.encode(), subsequence.seq.encode()))

    # Generate the phylogenetic tree
    aligner = Aligner(guide_tree="upgma")
    msa = aligner.align(sequences)

    bio_msa = []
    for sequence in msa:
        bio_seq = SeqRecord(Seq(sequence.sequence.decode()), id=sequence.id.decode())
        bio_msa.append(bio_seq)
    bio_msa = MultipleSeqAlignment(bio_msa)

    calculator = DistanceCalculator("identity")
    dist_matrix = calculator.get_distance(bio_msa)

    constructor = DistanceTreeConstructor()
    tree = constructor.nj(dist_matrix)

    # Prepare the domain architecture data if show_domains is True and at least one protein has a domain architecture
    if show_domains and not selected_dataframe["pfam_architecture"].isnull().all():
        domain_architecture = selected_dataframe.drop_duplicates(subset="target_name", keep="first")
    else:
        domain_architecture = None

    # Plot the phylogenetic tree
    fig = plot_tree(tree, domain_architecture)

    return fig
